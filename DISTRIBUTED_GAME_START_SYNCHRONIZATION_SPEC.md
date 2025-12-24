# Distributed Game Start Synchronization - Specification Document

## Overview

This document specifies the implementation of start synchronization for distributed multiplayer games in SGE, allowing games to start when the minimum number of players is reached (for range configurations like `num_players=(2,4)`), with proper synchronization between all instances.

**Key Principle**: The start synchronization system builds upon the existing distributed game infrastructure, extending it with minimum/maximum player handling and synchronized game start capabilities.

## Problem Statement

### Current Issues

1. **Minimum not respected**: With `num_players=(2,4)`, the system waits for 4 instances (maximum) before enabling "Start Now" button
2. **Button visibility**: "Start Now" button appears on all instances (both creator and joiners), not just the session creator
3. **Auto-countdown timing**: Auto-countdown only triggers at maximum (4), not at minimum (2)
4. **No start synchronization**: When "Start Now" is clicked or countdown finishes, each instance starts independently without synchronization
5. **No instance count access**: No way to retrieve the number of connected instances after `enableDistributedGame()`

### Requirements

1. **Minimum-based start**: "Start Now" button must appear when minimum (2) is reached, but only on the session creator instance
2. **Maximum-based auto-start**: Auto-countdown only triggers when maximum (4) is reached
3. **Synchronized start**: All instances must start together when "Start Now" is clicked or countdown finishes
4. **Instance count access**: Provide a modeler method to get the number of connected instances

## Solution Architecture

### 1. Minimum/Maximum Logic

**Location**: `SGDistributedConnectionDialog._updateConnectedInstances()`

**Changes**:
- Distinguish between minimum and maximum requirements
- Check minimum for "Start Now" button visibility
- Check maximum for auto-countdown trigger
- Update messages to reflect current state (minimum reached vs maximum reached)

### 2. Session Creator Identification

**Location**: `SGDistributedGameConfig` and `SGDistributedConnectionDialog`

**Changes**:
- Add `is_session_creator` attribute to `SGDistributedGameConfig`
- Set this flag when dialog is created (based on `create_new_radio.isChecked()`)
- Use this flag to control "Start Now" button visibility

### 3. Start Synchronization via MQTT

**Location**: `SGDistributedConnectionDialog` and `SGDistributedSessionManager`

**Changes**:
- Add `session_game_start` topic to `SGDistributedSessionManager.SESSION_TOPICS`
- Subscribe to `session_game_start` topic for all instances
- Publish start message when "Start Now" is clicked or countdown finishes (creator only)
- Handle start message in all instances to synchronize dialog closure

### 4. Instance Count Access

**Location**: `SGDistributedGameConfig` and `SGModel`

**Changes**:
- Add `connected_instances_count` attribute to `SGDistributedGameConfig`
- Update this count when instances connect/disconnect
- Add modeler method `getConnectedInstancesCount()` in `SGModel`

## Detailed Implementation Plan

### Phase 1: Configuration and State Management

#### 1.1 Add `is_session_creator` to `SGDistributedGameConfig`

**File**: `mainClasses/SGDistributedGameConfig.py`

**Changes**:
```python
def __init__(self):
    # ... existing attributes ...
    self.is_session_creator = False  # bool: True if this instance created the session
    self.connected_instances_count = 0  # int: Number of connected instances
```

**Validation**:
- [ ] `is_session_creator` defaults to `False`
- [ ] `connected_instances_count` defaults to `0`
- [ ] Attributes can be set and retrieved

#### 1.2 Set `is_session_creator` in Dialog

**File**: `mainClasses/SGDistributedConnectionDialog.py`

**Changes**:
In `__init__()` or after mode selection:
```python
# Set is_session_creator flag in config
if self.create_new_radio.isChecked():
    self.config.is_session_creator = True
else:
    self.config.is_session_creator = False
```

**Validation**:
- [ ] Flag is set correctly when creating new session
- [ ] Flag is set correctly when joining existing session
- [ ] Flag persists after dialog closes

### Phase 2: Minimum/Maximum Logic

#### 2.1 Update `_updateConnectedInstances()` Logic

**File**: `mainClasses/SGDistributedConnectionDialog.py`

**Current Code** (line 616-619):
```python
# Determine required number of instances
if isinstance(self.config.num_players, int):
    required_instances = self.config.num_players
else:
    required_instances = self.config.num_players_max  # ❌ Always uses max
```

**New Code**:
```python
# Determine minimum and maximum required instances
if isinstance(self.config.num_players, int):
    min_required = self.config.num_players
    max_required = self.config.num_players
else:
    min_required = self.config.num_players_min
    max_required = self.config.num_players_max

# Update connected_instances_count in config
self.config.connected_instances_count = num_instances

# Check if minimum is reached (for "Start Now" button)
min_reached = num_instances >= min_required

# Check if maximum is reached (for auto-countdown)
max_reached = num_instances >= max_required
```

**Validation**:
- [ ] Minimum is correctly identified for `num_players=(2,4)`
- [ ] Maximum is correctly identified for `num_players=(2,4)`
- [ ] `connected_instances_count` is updated correctly

#### 2.2 Update State Transitions

**File**: `mainClasses/SGDistributedConnectionDialog.py`

**Current Code** (line 638):
```python
if self.seed_synced and num_instances >= required_instances:
    # Always uses max_required
```

**New Code**:
```python
# Check if ready for manual start (minimum reached)
if self.seed_synced and min_reached:
    # Minimum reached - can start manually (if creator)
    if self.current_state != self.STATE_READY_MIN:
        self._updateState(self.STATE_READY_MIN)
    
    # Check if maximum reached (for auto-countdown)
    if max_reached:
        if self.current_state != self.STATE_READY_MAX:
            self._updateState(self.STATE_READY_MAX)
elif self.seed_synced:
    # Waiting for minimum
    if self.current_state != self.STATE_WAITING:
        self._updateState(self.STATE_WAITING)
```

**New States**:
- `STATE_READY_MIN`: Minimum reached, "Start Now" button available (creator only)
- `STATE_READY_MAX`: Maximum reached, auto-countdown triggers

**Validation**:
- [ ] `STATE_READY_MIN` is reached when minimum is met
- [ ] `STATE_READY_MAX` is reached when maximum is met
- [ ] States transition correctly as instances connect

### Phase 3: "Start Now" Button Visibility

#### 3.1 Update `_updateState()` for Button Visibility

**File**: `mainClasses/SGDistributedConnectionDialog.py`

**New State Handling**:
```python
elif new_state == self.STATE_READY_MIN:
    # Minimum reached - show "Start Now" button ONLY on creator instance
    self.session_id_edit.setEnabled(False)
    self.copy_session_btn.setEnabled(True)
    self.connect_button.hide()
    
    # CRITICAL: Show "Start Now" button ONLY if this is the session creator
    if self.config.is_session_creator:
        self.start_button.show()
        self.start_button.setEnabled(True)
        self.info_label.setText(
            f"✓ Minimum instances connected ({num_instances}/{min_required}-{max_required}). "
            f"Click 'Start Now' to begin, or wait for more players."
        )
    else:
        # Joiner instance - hide button, show waiting message
        self.start_button.hide()
        self.info_label.setText(
            f"✓ Minimum instances connected ({num_instances}/{min_required}-{max_required}). "
            f"Waiting for session creator to start the game..."
        )
    
    self.countdown_label.hide()
    # ... disable radio buttons, etc. ...

elif new_state == self.STATE_READY_MAX:
    # Maximum reached - auto-countdown will trigger
    self.session_id_edit.setEnabled(False)
    self.copy_session_btn.setEnabled(True)
    self.connect_button.hide()
    
    # CRITICAL: Show "Start Now" button ONLY on creator instance
    if self.config.is_session_creator:
        self.start_button.show()
        self.start_button.setEnabled(True)
    else:
        self.start_button.hide()
    
    self.info_label.setText("✓ All instances connected! The game will start automatically in a few seconds.")
    self._startAutoStartCountdown()  # Only triggers at maximum
```

**Validation**:
- [ ] "Start Now" button appears only on creator instance at minimum
- [ ] "Start Now" button appears only on creator instance at maximum
- [ ] Joiner instances see appropriate waiting messages
- [ ] Messages reflect current state (minimum vs maximum)

### Phase 4: Auto-Countdown Logic

#### 4.1 Update `_startAutoStartCountdown()` Trigger

**File**: `mainClasses/SGDistributedConnectionDialog.py`

**Current Code** (line 780):
```python
# Start countdown automatically for both create and join modes
self.info_label.setText("✓ All instances connected! The game will start automatically in a few seconds.")
self._startAutoStartCountdown()
```

**New Code**:
```python
# Auto-countdown ONLY triggers at STATE_READY_MAX (maximum reached)
# This is already handled in _updateState(STATE_READY_MAX)
# No changes needed to _startAutoStartCountdown() itself
```

#### 4.2 Update `_updateCountdown()` to Check Maximum

**File**: `mainClasses/SGDistributedConnectionDialog.py`

**Current Code** (line 1316-1319):
```python
if isinstance(self.config.num_players, int):
    required_instances = self.config.num_players
else:
    required_instances = self.config.num_players_max
```

**New Code**:
```python
# Check if still at maximum (countdown only runs at maximum)
if isinstance(self.config.num_players, int):
    required_instances = self.config.num_players
else:
    required_instances = self.config.num_players_max  # Check maximum, not minimum

# If instances drop below maximum, stop countdown
if num_instances < required_instances:
    # Not ready anymore, stop countdown
    if self.auto_start_timer:
        self.auto_start_timer.stop()
    self.countdown_label.hide()
    # Transition back to STATE_READY_MIN or STATE_WAITING
    if num_instances >= self.config.num_players_min:
        self._updateState(self.STATE_READY_MIN)
    else:
        self._updateState(self.STATE_WAITING)
    return
```

**Validation**:
- [ ] Countdown only starts at maximum
- [ ] Countdown stops if instance disconnects
- [ ] State transitions correctly when countdown stops

### Phase 5: Start Synchronization via MQTT

#### 5.1 Add `game_start` to SESSION_TOPICS

**File**: `mainClasses/SGDistributedSessionManager.py`

**Changes**:
```python
# Centralized list of session topics (base names without prefixes)
SESSION_TOPICS = ['player_registration', 'seed_sync', 'player_disconnect', 'game_start']
```

**Validation**:
- [ ] `game_start` is in `SESSION_TOPICS`
- [ ] `getSessionTopics()` returns correct topic with `session_` prefix

#### 5.2 Subscribe to `session_game_start` Topic

**File**: `mainClasses/SGDistributedConnectionDialog.py`

**New Method**:
```python
def _subscribeToGameStart(self):
    """Subscribe to game start topic for synchronization"""
    if not (self.model.mqttManager.client and 
            self.model.mqttManager.client.is_connected()):
        return
    
    # Get game start topic
    session_topics = self.session_manager.getSessionTopics(self.config.session_id)
    game_start_topic = f"{self.config.session_id}/session_game_start"
    
    # Get current handler (which is player_registration_tracking_wrapper)
    current_handler = self.model.mqttManager.client.on_message
    
    # Create wrapper to handle game start messages
    def game_start_handler(client, userdata, msg):
        # CRITICAL: Protect against RuntimeError if dialog is destroyed
        try:
            if msg.topic == game_start_topic:
                # Game start message received
                try:
                    import json
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    sender_client_id = msg_dict.get('clientId')
                    
                    # Ignore our own message (avoid loop)
                    if sender_client_id == self.model.mqttManager.clientId:
                        return
                    
                    # Check if already processed (avoid double processing)
                    if hasattr(self, '_game_start_processed') and self._game_start_processed:
                        return
                    
                    # Mark as processed
                    self._game_start_processed = True
                    
                    print(f"[Dialog] Game start signal received from {sender_client_id[:8]}..., closing dialog...")
                    
                    # Close dialog after short delay to allow message propagation
                    QTimer.singleShot(100, self.accept)
                    return
                except Exception as e:
                    print(f"[Dialog] Error processing game start message: {e}")
                    import traceback
                    traceback.print_exc()
                    return
        except RuntimeError:
            # Dialog has been deleted, ignore
            return
        
        # Forward other messages to current handler
        if current_handler:
            current_handler(client, userdata, msg)
    
    # Install wrapper
    self._game_start_handler = game_start_handler
    self.model.mqttManager.client.on_message = game_start_handler
    
    # Subscribe to game start topic
    self.model.mqttManager.client.subscribe(game_start_topic, qos=1)
    print(f"[Dialog] Subscribed to game start topic: {game_start_topic}")
    
    # Initialize processed flag
    self._game_start_processed = False
```

**Integration**:
Call `_subscribeToGameStart()` in `_syncSeed()` after `_subscribeToPlayerRegistrationForTracking()`:
```python
# In _syncSeed(), after line 964:
self._subscribeToPlayerRegistrationForTracking()

# CRITICAL: Subscribe to game start topic for synchronization
self._subscribeToGameStart()
```

**Validation**:
- [ ] All instances subscribe to `session_game_start` topic
- [ ] Handler is in the chain (wraps `player_registration_tracking_wrapper`)
- [ ] Handler forwards other messages correctly
- [ ] Protection against RuntimeError works

#### 5.3 Publish Game Start Message

**File**: `mainClasses/SGDistributedConnectionDialog.py`

**New Method**:
```python
def _publishGameStartMessage(self, start_type="manual"):
    """
    Publish game start message to synchronize all instances.
    
    Args:
        start_type (str): "manual" (button clicked) or "auto" (countdown finished)
    """
    if not (self.model.mqttManager.client and 
            self.model.mqttManager.client.is_connected()):
        return
    
    # Get game start topic
    session_topics = self.session_manager.getSessionTopics(self.config.session_id)
    game_start_topic = f"{self.config.session_id}/session_game_start"
    
    # Create start message
    from datetime import datetime
    start_msg = {
        'clientId': self.model.mqttManager.clientId,
        'timestamp': datetime.now().isoformat(),
        'start_type': start_type,  # "manual" or "auto"
        'countdown_finished': (start_type == "auto")
    }
    
    import json
    serialized_msg = json.dumps(start_msg)
    
    # CRITICAL: Publish with retain=False (we don't want old start messages)
    # Use QoS=1 to ensure delivery
    self.model.mqttManager.client.publish(
        game_start_topic, 
        serialized_msg, 
        qos=1,
        retain=False  # Don't retain - start message is one-time only
    )
    
    print(f"[Dialog] Published game start signal (type: {start_type}) to {game_start_topic}")
```

**Integration in Button Click**:
```python
def _onStartNowClicked(self):
    """Handle Start Now button click"""
    # Only creator can click this button (UI enforces this)
    if not self.config.is_session_creator:
        return
    
    # Publish start message
    self._publishGameStartMessage(start_type="manual")
    
    # Wait for message propagation (300-500ms recommended)
    QTimer.singleShot(300, self.accept)
```

**Integration in Countdown**:
```python
def _updateCountdown(self):
    # ... existing countdown logic ...
    
    if self.auto_start_countdown == 0:
        # Countdown finished - publish start message (creator only)
        if self.config.is_session_creator:
            self._publishGameStartMessage(start_type="auto")
        
        # Wait for message propagation
        QTimer.singleShot(300, self.accept)
        return
```

**Validation**:
- [ ] Message is published with correct format
- [ ] Message is published only by creator instance
- [ ] Message uses `retain=False` (one-time only)
- [ ] Delay before `accept()` allows message propagation

### Phase 6: Instance Count Access

#### 6.1 Update `connected_instances_count` in Config

**File**: `mainClasses/SGDistributedConnectionDialog.py`

**Changes**:
In `_updateConnectedInstances()`:
```python
# Update connected_instances_count in config
num_instances = len(instances_to_count)
self.config.connected_instances_count = num_instances
```

**Validation**:
- [ ] `connected_instances_count` is updated when instances connect
- [ ] `connected_instances_count` is updated when instances disconnect
- [ ] Count is accurate at all times

#### 6.2 Add Modeler Method `getConnectedInstancesCount()`

**File**: `mainClasses/SGModel.py`

**Location**: In GET/NB METHODS section

**New Method**:
```python
# ============================================================================
# GET/NB METHODS
# ============================================================================

def getConnectedInstancesCount(self):
    """
    Get the number of connected instances in distributed game mode.
    
    Returns:
        int: Number of connected instances, or 0 if not in distributed mode
    
    Example:
        count = myModel.getConnectedInstancesCount()
        if count >= 2:
            print("Minimum players reached!")
    """
    if not self.isDistributed():
        return 0
    
    if (hasattr(self, 'distributedConfig') and 
        self.distributedConfig and 
        hasattr(self.distributedConfig, 'connected_instances_count')):
        return self.distributedConfig.connected_instances_count
    
    return 0
```

**Validation**:
- [ ] Method returns correct count in distributed mode
- [ ] Method returns 0 in local mode
- [ ] Method is accessible to modelers

## Implementation Order

### Step 1: Configuration (Phase 1)
1. Add `is_session_creator` and `connected_instances_count` to `SGDistributedGameConfig`
2. Set `is_session_creator` in dialog initialization
3. **Test**: Verify flags are set correctly

### Step 2: Minimum/Maximum Logic (Phase 2)
1. Update `_updateConnectedInstances()` to distinguish min/max
2. Add `STATE_READY_MIN` and `STATE_READY_MAX` states
3. Update state transitions
4. **Test**: Verify states transition correctly

### Step 3: Button Visibility (Phase 3)
1. Update `_updateState()` for new states
2. Add conditional button visibility based on `is_session_creator`
3. Update messages
4. **Test**: Verify button appears only on creator

### Step 4: Auto-Countdown (Phase 4)
1. Update `_startAutoStartCountdown()` to only trigger at maximum
2. Update `_updateCountdown()` to check maximum
3. **Test**: Verify countdown only triggers at maximum

### Step 5: Start Synchronization (Phase 5)
1. Add `game_start` to `SESSION_TOPICS`
2. Implement `_subscribeToGameStart()`
3. Implement `_publishGameStartMessage()`
4. Integrate in button click and countdown
5. **Test**: Verify all instances start together

### Step 6: Instance Count Access (Phase 6)
1. Update `connected_instances_count` in `_updateConnectedInstances()`
2. Add `getConnectedInstancesCount()` to `SGModel`
3. **Test**: Verify method returns correct count

## Critical Implementation Details

### 1. Handler Chain Protection

**Problem**: Handlers reference `self` (dialog), which may be destroyed.

**Solution**:
```python
def game_start_handler(client, userdata, msg):
    try:
        # Check if dialog still exists
        if not hasattr(self, 'seed_synced'):
            return  # Dialog destroyed
        
        # ... handler logic ...
    except RuntimeError:
        # Dialog has been deleted, ignore
        return
```

### 2. Message Retain Strategy

**Decision**: Use `retain=False` for `session_game_start` because:
- Start message is one-time only (not needed for late joiners)
- Prevents old start messages from triggering new games
- Reduces broker storage

**Alternative considered**: `retain=True` would ensure late subscribers receive the message, but could cause issues if message is not cleared.

### 3. Double Processing Protection

**Solution**: Use flag to prevent multiple `accept()` calls:
```python
self._game_start_processed = False  # Initialize in _subscribeToGameStart()

# In handler:
if hasattr(self, '_game_start_processed') and self._game_start_processed:
    return  # Already processed
self._game_start_processed = True
```

### 4. Timing Considerations

**Delay before `accept()`**:
- **300ms recommended**: Allows MQTT message to propagate to all instances
- Too short (< 100ms): Some instances may not receive message
- Too long (> 500ms): Unnecessary delay for user

**Message propagation**:
- MQTT QoS=1 ensures at-least-once delivery
- Broker typically delivers within 50-200ms
- 300ms provides safety margin

### 5. State Management

**New States**:
- `STATE_READY_MIN`: Minimum reached, manual start available (creator only)
- `STATE_READY_MAX`: Maximum reached, auto-countdown triggers

**State Transitions**:
```
SETUP → CONNECTING → WAITING → READY_MIN → READY_MAX
                                    ↑           ↓
                                    └───────────┘ (if instance disconnects)
```

### 6. Button Click Handler

**New Method**:
```python
def _onStartNowClicked(self):
    """Handle Start Now button click - only available on creator instance"""
    if not self.config.is_session_creator:
        return  # Safety check (button should be hidden anyway)
    
    # Validate minimum is reached
    if isinstance(self.config.num_players, int):
        min_required = self.config.num_players
    else:
        min_required = self.config.num_players_min
    
    num_instances = len(self.connected_instances_snapshot or self.connected_instances)
    if num_instances < min_required:
        QMessageBox.warning(
            self,
            "Insufficient Instances",
            f"Only {num_instances} instance(s) connected, but {min_required} required."
        )
        return
    
    # Publish start message
    self._publishGameStartMessage(start_type="manual")
    
    # Wait for propagation, then close
    QTimer.singleShot(300, self.accept)
```

**Integration**:
```python
# In _buildUI(), change button connection:
self.start_button.clicked.connect(self._onStartNowClicked)  # Instead of self.accept
```

## Validation Checklist

### Phase 1: Configuration
- [ ] `is_session_creator` is set correctly
- [ ] `connected_instances_count` is initialized to 0
- [ ] Flags persist after dialog closes

### Phase 2: Minimum/Maximum Logic
- [ ] Minimum is correctly identified for `num_players=(2,4)`
- [ ] Maximum is correctly identified for `num_players=(2,4)`
- [ ] `connected_instances_count` is updated correctly
- [ ] States transition correctly (WAITING → READY_MIN → READY_MAX)

### Phase 3: Button Visibility
- [ ] "Start Now" appears only on creator at minimum
- [ ] "Start Now" appears only on creator at maximum
- [ ] Joiner instances see appropriate messages
- [ ] Messages reflect current state

### Phase 4: Auto-Countdown
- [ ] Countdown only starts at maximum
- [ ] Countdown stops if instance disconnects
- [ ] State transitions correctly when countdown stops

### Phase 5: Start Synchronization
- [ ] All instances subscribe to `session_game_start`
- [ ] Handler is in the chain
- [ ] Message is published by creator only
- [ ] All instances receive message and close dialog together
- [ ] Protection against RuntimeError works
- [ ] Double processing is prevented

### Phase 6: Instance Count Access
- [ ] `getConnectedInstancesCount()` returns correct count
- [ ] Method returns 0 in local mode
- [ ] Count is updated in real-time

### End-to-End Tests

**Test 1: Minimum Start (2 instances, range 2-4)**
- [ ] Instance 1 (creator): Creates session, connects
- [ ] Instance 2 (joiner): Joins session, connects
- [ ] Instance 1: "Start Now" button appears (minimum reached)
- [ ] Instance 2: No "Start Now" button, sees waiting message
- [ ] Instance 1: Clicks "Start Now"
- [ ] Both instances: Receive start message, close dialog together
- [ ] Both instances: Game starts synchronously

**Test 2: Maximum Auto-Start (4 instances, range 2-4)**
- [ ] Instances 1-4: All connect
- [ ] Instance 1: "Start Now" button visible (can start manually)
- [ ] All instances: Auto-countdown starts (maximum reached)
- [ ] All instances: Receive start message when countdown finishes
- [ ] All instances: Close dialog together, game starts synchronously

**Test 3: Countdown Interruption**
- [ ] 4 instances connected, countdown running
- [ ] Instance 4: Disconnects
- [ ] Countdown: Stops immediately
- [ ] State: Transitions back to READY_MIN or WAITING

**Test 4: Instance Count Access**
- [ ] After `enableDistributedGame()`, call `getConnectedInstancesCount()`
- [ ] Verify count matches actual connected instances
- [ ] Verify count updates as instances connect/disconnect

## Error Handling

### 1. Handler RuntimeError Protection

**Scenario**: Dialog is destroyed while handler is active.

**Solution**: Already implemented with `try/except RuntimeError` in handler.

### 2. Message Not Received

**Scenario**: Some instances don't receive start message.

**Mitigation**:
- Use QoS=1 for guaranteed delivery
- 300ms delay before `accept()` allows propagation
- If message is lost, user can manually close dialog (fallback)

### 3. Multiple Start Messages

**Scenario**: Multiple instances publish start message simultaneously.

**Solution**: 
- Only creator can publish (UI enforced)
- Flag prevents double processing
- Ignore own message in handler

### 4. Dialog Closed Before Message Received

**Scenario**: User closes dialog before start message is received.

**Solution**: 
- Handler checks if dialog exists before processing
- If dialog is closed, message is ignored (expected behavior)

## Backward Compatibility

### Existing Behavior Preserved

- **Fixed `num_players`**: Behavior unchanged (minimum = maximum = fixed value)
- **Local mode**: No impact (distributed mode is opt-in)
- **Legacy MQTT games**: No impact (uses different topics)

### Breaking Changes

**None**: All changes are additive and backward compatible.

## Performance Considerations

### MQTT Message Overhead

- **One message per start**: Minimal overhead
- **QoS=1**: Slight latency increase (acceptable for start synchronization)
- **No retain**: No broker storage overhead

### Handler Chain Performance

- **Additional wrapper**: Minimal performance impact
- **Topic check**: Fast string comparison
- **Message parsing**: Only for `session_game_start` topic

## Future Enhancements

### Potential Improvements

1. **Start confirmation**: Wait for acknowledgment from all instances before starting
2. **Start timeout**: If some instances don't respond, show warning and allow manual override
3. **Start retry**: Retry mechanism if message delivery fails
4. **Start logging**: Log start events for debugging

## Notes

- All code and docstrings must be in English
- Follow existing SGE coding conventions
- Maintain separation of concerns (session topics vs game topics)
- Test thoroughly with 2, 3, and 4 instances
- Ensure no regression in existing distributed game functionality


