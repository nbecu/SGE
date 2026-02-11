"""
SGStateSnapshot - World state serialization for recovery, backward/forward, and replay.

Format: JSON with format_version, metadata, entities (agents, cells, tiles), players,
simulation_variables. Players include dict_attributes and per-game-action data. Entity/player
history["value"]: not included when writing to disk (recovery/session); on restore we trim
to (round, phase) <= current so graphs do not see "future" steps. For backward/redo stack,
call build_snapshot_from_model(model, include_history_value=True) so snapshots carry
history["value"] and redo restores it correctly (graphs then work for both backward and redo). Stable IDs for entities; JSON-serializable attribute values only (QColor -> hex).
PyQt5/PyQt6: value conversion uses duck-typing (e.g. obj.name()) to avoid hard Qt import.
"""

import gzip
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime

FORMAT_VERSION = 1


def _attribute_value_to_json(val):
    """
    Convert an attribute value to a JSON-serializable type.
    Excludes non-serializable types; converts QColor-like (has .name()) to hex string.
    """
    if val is None:
        return None
    if isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, (list, tuple)):
        return [_attribute_value_to_json(v) for v in val]
    if isinstance(val, dict):
        return {k: _attribute_value_to_json(v) for k, v in val.items()}
    # QColor-like: has .name() returning hex (PyQt5/PyQt6 compatible)
    if hasattr(val, "name") and callable(val.name):
        try:
            return val.name()
        except Exception:
            return str(val)
    # Fallback: try str (may lose type on load)
    try:
        json.dumps(val)
        return val
    except (TypeError, ValueError):
        return str(val)


def _entity_dict_attributes_to_json(dict_attributes):
    """Serialize dictAttributes to JSON-safe dict."""
    if not dict_attributes:
        return {}
    return {
        str(k): _attribute_value_to_json(v)
        for k, v in dict_attributes.items()
    }


def _history_value_to_json(history_value):
    """
    Serialize entity/player history["value"] for snapshot (backward/redo stack).
    history_value: dict att -> list of [round, phase, value].
    Returns JSON-serializable dict.
    """
    if not history_value:
        return {}
    out = {}
    for att, lst in history_value.items():
        if not isinstance(lst, list):
            continue
        out[str(att)] = [
            [e[0], e[1], _attribute_value_to_json(e[2])]
            for e in lst
            if len(e) >= 3
        ]
    return out


def build_snapshot_from_model(model, include_history_value=False):
    """
    Build a world state snapshot dict from the given SGModel.
    include_history_value: if True, add history["value"] for entities/players (for backward/redo
    stack so that redo restores full history and graph interfaces do not break).
    Returns a dict matching the snapshot schema (format_version, entities, etc.).
    """
    time_mgr = model.timeManager
    current_phase = time_mgr.getCurrentPhase() if time_mgr.phases else None
    phase_name = current_phase.name if current_phase and hasattr(current_phase, "name") else ""

    snapshot = {
        "format_version": FORMAT_VERSION,
        "model_name": getattr(model, "name", None) or getattr(model, "windowTitle", "Unnamed Model"),
        "timestamp": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "round": time_mgr.currentRoundNumber,
        "phase": time_mgr.currentPhaseNumber,
        "phase_name": phase_name,
        "entities": {
            "agents": [],
            "cells": [],
            "tiles": [],
        },
        "players": [],
        "simulation_variables": [],
        "current_player_name": getattr(model, "currentPlayerName", None) or "",
    }

    # Cells (each cellType has a grid; entities are cells)
    for cell_type in model.cellTypes.values():
        type_name = cell_type.name
        for cell in cell_type.entities:
            try:
                cell_id = cell.getId() if hasattr(cell, "getId") and callable(cell.getId) else (cell.id if hasattr(cell, "id") else None)
                x = getattr(cell, "xCoord", None)
                y = getattr(cell, "yCoord", None)
                dict_attrs = getattr(cell, "dictAttributes", None) or {}
                entry = {
                    "type_name": type_name,
                    "id": cell_id,
                    "x": x,
                    "y": y,
                    "dict_attributes": _entity_dict_attributes_to_json(dict_attrs),
                }
                if include_history_value:
                    hv = getattr(cell, "history", {}).get("value") or {}
                    entry["history_value"] = _history_value_to_json(hv)
                snapshot["entities"]["cells"].append(entry)
            except Exception:
                continue

    # Agents
    for agent_type in model.agentTypes.values():
        type_name = agent_type.name
        for agent in agent_type.entities:
            try:
                cell = getattr(agent, "cell", None)
                cell_id = cell.getId() if cell and hasattr(cell, "getId") and callable(cell.getId) else None
                x, y = cell.getCoords() if cell and hasattr(cell, "getCoords") and callable(cell.getCoords) else (None, None)
                dict_attrs = getattr(agent, "dictAttributes", None) or {}
                entry = {
                    "type_name": type_name,
                    "id": agent.id,
                    "cell_id": cell_id,
                    "x": x,
                    "y": y,
                    "dict_attributes": _entity_dict_attributes_to_json(dict_attrs),
                }
                if include_history_value:
                    hv = getattr(agent, "history", {}).get("value") or {}
                    entry["history_value"] = _history_value_to_json(hv)
                snapshot["entities"]["agents"].append(entry)
            except Exception:
                continue

    # Tiles
    for tile_type in model.tileTypes.values():
        type_name = tile_type.name
        for tile in tile_type.entities:
            try:
                cell = getattr(tile, "cell", None)
                cell_id = cell.getId() if cell and hasattr(cell, "getId") and callable(cell.getId) else None
                face = getattr(tile, "face", "front")
                stack_index = 0
                if cell and hasattr(cell, "tiles"):
                    try:
                        stack_index = cell.tiles.index(tile) if tile in cell.tiles else 0
                    except (ValueError, AttributeError):
                        pass
                dict_attrs = getattr(tile, "dictAttributes", None) or {}
                entry = {
                    "type_name": type_name,
                    "id": tile.id,
                    "cell_id": cell_id,
                    "face": face,
                    "stack_index": stack_index,
                    "dict_attributes": _entity_dict_attributes_to_json(dict_attrs),
                }
                if include_history_value:
                    hv = getattr(tile, "history", {}).get("value") or {}
                    entry["history_value"] = _history_value_to_json(hv)
                snapshot["entities"]["tiles"].append(entry)
            except Exception:
                continue

    # Players: attributes and game action usage counters
    for player in getattr(model, "players", {}).values():
        try:
            player_name = getattr(player, "name", None)
            if not player_name:
                continue
            dict_attrs = getattr(player, "dictAttributes", None) or {}
            game_actions_data = []
            for action in getattr(player, "gameActions", []) or []:
                action_id = getattr(action, "id", None)
                number_used = getattr(action, "numberUsed", 0)
                total_number_used = getattr(action, "totalNumberUsed", 0)
                # history["performed"] is used by DataRecorder.getStepsData_ofGameActions(); store [round, phase] per performance
                performed = getattr(action, "history", {}).get("performed") or []
                history_performed = [[e[0], e[1]] for e in performed if len(e) >= 2]
                game_actions_data.append({
                    "action_id": action_id,
                    "number_used": number_used,
                    "total_number_used": total_number_used,
                    "history_performed": history_performed,
                })
            player_entry = {
                "name": player_name,
                "dict_attributes": _entity_dict_attributes_to_json(dict_attrs),
                "game_actions": game_actions_data,
            }
            if include_history_value:
                hv = getattr(player, "history", {}).get("value") or {}
                player_entry["history_value"] = _history_value_to_json(hv)
            snapshot["players"].append(player_entry)
        except Exception:
            continue

    # Simulation variables
    for sim_var in getattr(model, "simulationVariables", []) or []:
        name = getattr(sim_var, "name", None)
        value = getattr(sim_var, "value", None)
        if name is not None:
            snapshot["simulation_variables"].append({
                "name": name,
                "value": _attribute_value_to_json(value),
            })

    return snapshot


def write_snapshot_to_file(snapshot, filepath, use_gzip=False):
    """
    Write snapshot dict to file. Atomic write: temp file then rename.
    filepath: final path (.json or .json.gz).
    use_gzip: if True, write gzip-compressed (filepath should end with .json.gz).
    """
    dirpath = os.path.dirname(filepath)
    if dirpath and not os.path.isdir(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    suffix = ".json.gz.tmp" if use_gzip else ".json.tmp"
    fd, tmp_path = tempfile.mkstemp(dir=dirpath or ".", prefix="sge_snapshot_", suffix=suffix)
    try:
        json_str = json.dumps(snapshot, ensure_ascii=False, indent=2)
        if use_gzip:
            with os.fdopen(fd, "wb") as f:
                with gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as gz:
                    gz.write(json_str.encode("utf-8"))
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json_str)
        os.replace(tmp_path, filepath)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise


def read_snapshot_from_file(filepath):
    """
    Read snapshot from file. Supports .json and .json.gz.
    Returns snapshot dict. Raises if file invalid or format_version unknown.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Snapshot file not found: {filepath}")
    if filepath.lower().endswith(".gz"):
        with gzip.open(filepath, "rt", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    version = data.get("format_version")
    if version is None:
        raise ValueError("Invalid snapshot: missing format_version")
    if version != FORMAT_VERSION:
        raise ValueError(f"Unsupported snapshot format_version: {version} (expected {FORMAT_VERSION})")
    return data


def load_snapshot_array_from_json_gz(filepath):
    """
    Load a JSON array of snapshots from a .json.gz file (saved_sessions format).
    Returns list of snapshot dicts.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Session file not found: {filepath}")
    with gzip.open(filepath, "rt", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Saved session file must contain a JSON array of snapshots")
    for i, item in enumerate(data):
        if item.get("format_version") != FORMAT_VERSION:
            raise ValueError(f"Unsupported format_version at index {i}: {item.get('format_version')}")
    return data


def _find_cell_by_id(model, cell_id):
    """Return (cell, cell_type) for the cell with getId() == cell_id, or (None, None)."""
    for cell_type in model.cellTypes.values():
        for cell in cell_type.entities:
            if hasattr(cell, "getId") and callable(cell.getId) and cell.getId() == cell_id:
                return cell, cell_type
    return None, None


def _trim_history_value_to_step(obj, current_round, current_phase):
    """
    Trim obj.history["value"] so that only entries at or before (current_round, current_phase) remain.
    Avoids graph interfaces seeing "future" steps after a backward or load.
    """
    history_val = getattr(obj, "history", None)
    if not isinstance(history_val, dict) or "value" not in history_val:
        return
    for att, lst in list(history_val["value"].items()):
        if not isinstance(lst, list):
            continue
        # Keep [r, p, v] where (r, p) <= (current_round, current_phase)
        history_val["value"][att] = [
            e for e in lst
            if len(e) >= 3 and (e[0], e[1]) <= (current_round, current_phase)
        ]


def apply_snapshot_to_model(model, snapshot):
    """
    Restore model state from a snapshot dict (e.g. from read_snapshot_from_file).
    Updates simulation variables, time (round/phase), current player, and entity
    attributes/positions. Assumes model structure (entity types and counts) is
    unchanged; only attributes and positions are restored (stable IDs).
    """
    # Simulation variables
    for sv_data in snapshot.get("simulation_variables") or []:
        name = sv_data.get("name")
        value = sv_data.get("value")
        if name is None:
            continue
        for sim_var in getattr(model, "simulationVariables", []) or []:
            if getattr(sim_var, "name", None) == name:
                sim_var.setValue_silently(value)
                break

    # Time and current player
    time_mgr = model.timeManager
    time_mgr.currentRoundNumber = snapshot.get("round", time_mgr.currentRoundNumber)
    time_mgr.currentPhaseNumber = snapshot.get("phase", time_mgr.currentPhaseNumber)
    if hasattr(model, "setCurrentPlayer") and callable(model.setCurrentPlayer):
        player_name = snapshot.get("current_player_name") or ""
        if player_name:
            model.setCurrentPlayer(player_name)

    # Players: dict_attributes and game action usage counters (and optional history_value)
    players_data = snapshot.get("players") or []
    model_players = getattr(model, "players", {}) or {}
    for pdata in players_data:
        pname = pdata.get("name")
        if not pname or pname not in model_players:
            continue
        player = model_players[pname]
        dict_attrs = pdata.get("dict_attributes") or {}
        has_hv = "history_value" in pdata and pdata["history_value"]
        if has_hv:
            hv_data = pdata.get("history_value") or {}
            if hasattr(player, "history") and isinstance(player.history, dict):
                player.history["value"] = defaultdict(list, {
                    str(att): list(entries) for att, entries in hv_data.items()
                })
            for att, val in dict_attrs.items():
                if hasattr(player, "dictAttributes"):
                    player.dictAttributes[att] = val
        else:
            for att, val in dict_attrs.items():
                try:
                    player.setValue(att, val)
                except Exception:
                    pass
        for ga_data in pdata.get("game_actions") or []:
            action_id = ga_data.get("action_id")
            number_used = ga_data.get("number_used", 0)
            total_number_used = ga_data.get("total_number_used", 0)
            history_performed = ga_data.get("history_performed") or []
            for action in getattr(player, "gameActions", []) or []:
                if getattr(action, "id", None) == action_id:
                    action.numberUsed = number_used
                    action.totalNumberUsed = total_number_used
                    # Restore history["performed"] so DataRecorder.getStatsOfGameActions() counts are correct
                    if hasattr(action, "history") and isinstance(action.history, dict):
                        action.history["performed"] = [
                            [r, p, 0, None, None, None, "", 0, ""]
                            for r, p in history_performed
                        ]
                    break

    # Cells: match by type_name and id (from getId), set dict_attributes (and optional history_value)
    for cell_data in snapshot.get("entities", {}).get("cells") or []:
        type_name = cell_data.get("type_name")
        x, y = cell_data.get("x"), cell_data.get("y")
        dict_attrs = cell_data.get("dict_attributes") or {}
        if not type_name or x is None or y is None:
            continue
        try:
            cell_type = model.getEntityType(type_name)
            cell = cell_type.getCell(x, y)
            if not cell:
                continue
            has_hv = "history_value" in cell_data and cell_data["history_value"]
            if has_hv:
                hv_data = cell_data.get("history_value") or {}
                if hasattr(cell, "history") and isinstance(cell.history, dict):
                    cell.history["value"] = defaultdict(list, {
                        str(att): list(entries) for att, entries in hv_data.items()
                    })
                for att, val in dict_attrs.items():
                    if hasattr(cell, "dictAttributes"):
                        cell.dictAttributes[att] = val
            elif dict_attrs:
                for att, val in dict_attrs.items():
                    cell.setValue(att, val)
        except Exception:
            continue

    # Agents: match by type_name and id, set cell (moveTo) and dict_attributes
    for agent_data in snapshot.get("entities", {}).get("agents") or []:
        type_name = agent_data.get("type_name")
        eid = agent_data.get("id")
        cell_id = agent_data.get("cell_id")
        dict_attrs = agent_data.get("dict_attributes") or {}
        if not type_name or eid is None:
            continue
        try:
            agent_type = model.getEntityType(type_name)
            agent = next((a for a in agent_type.entities if a.id == eid), None)
            if not agent:
                continue
            cell, _ = _find_cell_by_id(model, cell_id)
            if cell and getattr(agent, "cell", None) != cell:
                agent.moveTo(cell)
                if hasattr(agent, "view") and agent.view:
                    agent.view.show()
            has_hv = "history_value" in agent_data and agent_data["history_value"]
            if has_hv:
                hv_data = agent_data.get("history_value") or {}
                if hasattr(agent, "history") and isinstance(agent.history, dict):
                    agent.history["value"] = defaultdict(list, {
                        str(att): list(entries) for att, entries in hv_data.items()
                    })
                for att, val in dict_attrs.items():
                    if hasattr(agent, "dictAttributes"):
                        agent.dictAttributes[att] = val
            elif dict_attrs:
                for att, val in dict_attrs.items():
                    agent.setValue(att, val)
        except Exception:
            continue

    # Tiles: match by type_name and id, set cell (moveTo), face, dict_attributes
    for tile_data in snapshot.get("entities", {}).get("tiles") or []:
        type_name = tile_data.get("type_name")
        eid = tile_data.get("id")
        cell_id = tile_data.get("cell_id")
        face = tile_data.get("face", "front")
        dict_attrs = tile_data.get("dict_attributes") or {}
        if not type_name or eid is None:
            continue
        try:
            tile_type = model.getEntityType(type_name)
            tile = next((t for t in tile_type.entities if t.id == eid), None)
            if not tile:
                continue
            cell, _ = _find_cell_by_id(model, cell_id)
            if cell and getattr(tile, "cell", None) != cell:
                tile.moveTo(cell)
                if hasattr(tile, "view") and tile.view:
                    tile.view.show()
            if getattr(tile, "face", None) != face and hasattr(tile, "setFace"):
                tile.setFace(face)
            has_hv = "history_value" in tile_data and tile_data["history_value"]
            if has_hv:
                hv_data = tile_data.get("history_value") or {}
                if hasattr(tile, "history") and isinstance(tile.history, dict):
                    tile.history["value"] = defaultdict(list, {
                        str(att): list(entries) for att, entries in hv_data.items()
                    })
                for att, val in dict_attrs.items():
                    if hasattr(tile, "dictAttributes"):
                        tile.dictAttributes[att] = val
            elif dict_attrs:
                for att, val in dict_attrs.items():
                    tile.setValue(att, val)
        except Exception:
            continue

    # Trim entity/player history["value"] to current step so graph interfaces don't see "future" data
    current_round = time_mgr.currentRoundNumber
    current_phase = time_mgr.currentPhaseNumber
    for cell_type in getattr(model, "cellTypes", {}).values():
        for cell in getattr(cell_type, "entities", []) or []:
            _trim_history_value_to_step(cell, current_round, current_phase)
    for agent_type in getattr(model, "agentTypes", {}).values():
        for agent in getattr(agent_type, "entities", []) or []:
            _trim_history_value_to_step(agent, current_round, current_phase)
    for tile_type in getattr(model, "tileTypes", {}).values():
        for tile in getattr(tile_type, "entities", []) or []:
            _trim_history_value_to_step(tile, current_round, current_phase)
    for player in (getattr(model, "players", {}) or {}).values():
        _trim_history_value_to_step(player, current_round, current_phase)
