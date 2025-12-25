# Specification: Player Reservation System for Distributed Games

## 1. Overview

This specification describes the implementation of a player reservation system that prevents multiple instances from selecting the same player in distributed multiplayer games. The system provides real-time visibility of player availability across all instances and handles conflict resolution.

## 2. Objectives

- **Prevent conflicts**: Ensure that two instances cannot select the same player simultaneously
- **Real-time visibility**: Show which players are already taken on all instances' interfaces
- **Conflict handling**: Detect and handle conflicts gracefully with user-friendly error messages
- **Player change**: Allow users to change their selected player before the game starts

## 3. MQTT Architecture

### 3.1 New Topic

**Topic Name**: `{session_id}/session_player_reservation`

**Topic Structure**: 
- Base topic: `{session_id}/session_player_reservation`
- Per-player topic: `{session_id}/session_player_reservation/{player_name}`
- Wildcard subscription: `{session_id}/session_player_reservation/+`

**Message Retention**: `retain=True` (all reservation messages are retained)

**QoS Level**: `qos=1` (at least once delivery)

### 3.2 Message Format

**Reservation Message**:
```json
{
  "clientId": "uuid-of-instance",
  "player_name": "Player1",
  "action": "reserve",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Release Message**:
```json
{
  "clientId": "uuid-of-instance",
  "player_name": "Player1",
  "action": "release",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 3.3 Topic Registration

Add `'player_reservation'` to `SESSION_TOPICS` in `SGDistributedSessionManager`:
```python
SESSION_TOPICS = ['player_registration', 'seed_sync', 'player_disconnect', 'game_start', 'instance_ready', 'player_reservation']
```

## 4. Core Functionality

### 4.1 Reservation Process

**When a user selects a player:**

1. User clicks on a player in the "Choose Player" dialog
2. Instance immediately publishes a "reserve" message for that player
3. Wait 200-300ms to receive any concurrent reservation messages
4. Check if any other instance reserved the same player during the wait period
5. **If conflict detected:**
   - Display error message (see section 5.1)
   - Do NOT confirm the selection
   - Keep dialog open
   - Mark the conflicted player as "already taken" in the UI
   - Allow user to select another player
6. **If no conflict:**
   - Confirm the reservation
   - Update local UI to show this player as "selected by you"
   - Proceed with player assignment

### 4.2 Real-time Updates

**Subscription to reservations:**

- Each instance subscribes to: `{session_id}/session_player_reservation/+`
- Handler processes all reservation/release messages (retained + new)
- UI is updated in real-time when any reservation changes

**UI Updates:**

- When a reservation message is received:
  - If `action == "reserve"` and `clientId != own_clientId`:
    - Mark player as "already taken" (grayed out, non-clickable)
    - Update visual indicator
  - If `action == "release"`:
    - Mark player as "available" (normal button, clickable)
    - Update visual indicator

### 4.3 Conflict Detection

**Detection Mechanism:**

1. After user clicks a player, publish "reserve" message
2. Start a 200-300ms timer
3. During the timer, listen for messages on `session_player_reservation/{player_name}`
4. If a "reserve" message with different `clientId` is received → conflict detected
5. If no conflicting message received → no conflict, proceed

**Conflict Resolution:**

- When conflict is detected:
  - Display error message (see section 5.1)
  - Do NOT confirm selection
  - Mark player as "already taken" immediately
  - Allow user to select another player

**Note**: We do NOT implement priority-based conflict resolution (first-come-first-served). Instead, we simply inform the user and let them choose another player.

### 4.4 Player Release

**When to release a reservation:**

1. **User cancels selection**: When user clicks "Cancel" or closes dialog without confirming
2. **User changes player**: When user selects a different player (release old, reserve new)
3. **Instance disconnects**: Use MQTT "last will" or explicit disconnect handler
4. **Game starts**: All reservations are finalized (no more changes allowed)

**Release Process:**

1. Publish "release" message on `session_player_reservation/{player_name}`
2. Set `retain=True` to clear the retained reservation message
3. Other instances receive the release and update their UI

## 5. User Interface

### 5.1 Error Message (Conflict Detection)

**Implementation:**
- Use `QMessageBox.information()` (not warning or error)
- Title: **"Player already selected"** (in English, as SGE is in English)
- Message: "This player has just been selected by another instance. Please choose another player."
- Auto-close: Automatically closes after 3 seconds
- Modal: Blocks interaction until closed (or auto-closed)

**Technical Implementation:**
```python
msg_box = QMessageBox.information(
    self,
    "Player already selected",
    "This player has just been selected by another instance. Please choose another player."
)
# Auto-close after 3 seconds
QTimer.singleShot(3000, msg_box.close)
```

### 5.2 Player States in UI

**Available Player:**
- Button: Normal style, clickable
- Text: Player name (e.g., "Player1")
- Color: Default button color
- Action: Click to select

**Reserved by Another Instance:**
- Button: Grayed out, non-clickable
- Text: "Player1 - Already taken"
- Color: Gray/disabled style
- Icon: Optional "lock" or "taken" indicator
- Action: None (button disabled)

**Selected by This Instance:**
- Button: Highlighted/colored, clickable (to cancel if needed)
- Text: "Player1 - You have selected"
- Color: Highlighted style (e.g., green or blue)
- Icon: Optional checkmark
- Action: Click to confirm (or cancel if change allowed)

**In Conflict (momentary):**
- Button: Error indicator (red/orange border or background)
- Text: "Player1 - Conflict detected"
- Duration: Brief (transitions to "Already taken" after error message)

### 5.3 Real-time UI Updates

**When reservation received:**
- Immediately update the player's visual state
- Disable button if reserved by another instance
- Enable button if released

**When own reservation confirmed:**
- Update selected player's appearance
- Optionally disable other player buttons (or keep them enabled for change)

### 5.4 Change Player Functionality

**Prerequisites:**
- User has already selected and confirmed a player
- Game has NOT started yet (dialog state: `connected_instances_snapshot is None`)

**UI Element:**
- Add button "Change Player" in the main interface (after player selection)
- Visible only before game starts
- Hidden/disabled once game starts

**Process:**
1. User clicks "Change Player"
2. Release current reservation (publish "release" for current player)
3. Reopen "Choose Player" dialog
4. Show all available players (including the one just released)
5. User selects new player
6. Same conflict detection process applies
7. If successful, update reservation and close dialog

**Dialog Management:**
- Do NOT destroy dialog after player selection
- Use `dialog.hide()` instead of `dialog.close()`
- Reuse same dialog instance when "Change Player" is clicked

## 6. Implementation Details

### 6.1 New Methods in SGDistributedSessionManager

**`reservePlayer(session_id, player_name)`**
- Publishes "reserve" message on `session_player_reservation/{player_name}`
- Uses `retain=True`, `qos=1`
- Returns: None (or success/failure status)

**`releasePlayer(session_id, player_name)`**
- Publishes "release" message on `session_player_reservation/{player_name}`
- Uses `retain=True` to clear retained message
- Returns: None

**`subscribeToPlayerReservations(session_id, callback)`**
- Subscribes to wildcard: `session_player_reservation/+`
- Calls `callback(client_id, player_name, action)` for each reservation message
- Handles both retained and new messages
- Returns: None

### 6.2 Modifications to "Choose Player" Dialog

**New Attributes:**
- `self.player_reservations = {}`  # {player_name: client_id} - tracks who reserved what
- `self.selected_player = None`  # Currently selected player (if any)
- `self.reservation_confirmed = False`  # Whether reservation is confirmed

**New Methods:**
- `_subscribeToPlayerReservations()`: Subscribe to reservation topic
- `_onPlayerReservationReceived(client_id, player_name, action)`: Handle reservation messages
- `_reservePlayer(player_name)`: Publish reservation and check for conflicts
- `_releasePlayer(player_name)`: Publish release message
- `_updatePlayerButtonState(player_name, state)`: Update UI for a specific player
- `_checkForConflict(player_name, wait_time_ms=250)`: Check for conflicts after reservation

**Modified Methods:**
- `_onPlayerSelected(player_name)`: Add conflict detection before confirmation
- Dialog close/hide: Release reservation if user cancels

### 6.3 Conflict Detection Implementation

**`_checkForConflict(player_name, wait_time_ms=250)`:**
1. Record current time
2. Publish "reserve" message
3. Start timer for `wait_time_ms` milliseconds
4. During timer, monitor incoming reservation messages for `player_name`
5. If message with different `clientId` received → return `True` (conflict)
6. If timer expires without conflict → return `False` (no conflict)

**Thread Safety:**
- Use `QTimer` for async conflict checking
- Use thread-safe flags to track conflict state
- Update UI using `QMetaObject.invokeMethod` if needed

### 6.4 Integration with Existing Flow

**In `completeDistributedGameSetup()` (SGModel):**
- After player selection dialog closes, check if player was selected
- If selected, proceed with game setup
- Keep reference to dialog for potential "Change Player" functionality

**In main interface (before game starts):**
- Display current player: "You are: {player_name}"
- Show "Change Player" button (if game not started)
- Hide/disable button once game starts

## 7. Edge Cases and Error Handling

### 7.1 Network Issues

**If MQTT connection lost during reservation:**
- Display error: "Connection lost. Please reconnect and try again."
- Do NOT confirm reservation
- Keep dialog open

**If reservation message not acknowledged:**
- Retry once after short delay
- If still fails, show error and allow retry

### 7.2 Timing Issues

**If multiple instances reserve simultaneously:**
- Both will detect conflict
- Both will show error message
- Both users can select different players

**If instance receives own reservation message:**
- Ignore it (check `clientId` before processing)
- Do NOT treat as conflict

### 7.3 Stale Reservations

**If instance disconnects without releasing:**
- Use MQTT "last will" to automatically release
- Or implement timeout mechanism (reservation expires after X minutes of inactivity)
- Other instances will see release and update UI

### 7.4 User Cancellation

**If user clicks "Cancel" after selecting:**
- Release any pending reservation
- Close dialog
- Do NOT proceed with game setup

**If user closes dialog (X button):**
- Same as Cancel: release reservation, close dialog

## 8. Testing Scenarios

### 8.1 Basic Functionality

1. **Single instance selects player:**
   - Player should be marked as "selected by you"
   - No conflicts
   - Reservation confirmed

2. **Two instances select different players:**
   - Both should succeed
   - No conflicts
   - Both players reserved

3. **Two instances select same player:**
   - Both should detect conflict
   - Both should see error message
   - Both should be able to select different players

### 8.2 Real-time Updates

1. **Instance A selects Player1:**
   - Instance B should see Player1 as "already taken" immediately
   - Instance B's UI should update without user action

2. **Instance A releases Player1:**
   - Instance B should see Player1 as "available" immediately
   - Instance B can now select Player1

### 8.3 Change Player

1. **User selects Player1, then clicks "Change Player":**
   - Player1 should be released
   - Dialog should reopen
   - Player1 should be available again
   - User can select any player (including Player1 again)

2. **User tries to change after game starts:**
   - "Change Player" button should be hidden/disabled
   - No action possible

### 8.4 Edge Cases

1. **Rapid clicks on same player:**
   - Should handle gracefully (debounce or ignore duplicate clicks)

2. **Network delay:**
   - Conflict detection should still work (250ms wait should be sufficient)

3. **Instance disconnects:**
   - Reservations should be released
   - Other instances should see players as available

## 9. Success Criteria

- ✅ No two instances can have the same player assigned
- ✅ All instances see real-time updates of player availability
- ✅ Conflicts are detected and handled gracefully
- ✅ Users can change their player before game starts
- ✅ Error messages are clear and user-friendly
- ✅ System handles network issues and edge cases
- ✅ UI is responsive and provides clear feedback

## 10. Future Enhancements (Out of Scope)

- Priority-based conflict resolution (first-come-first-served)
- Player reservation timeout/expiration
- Reservation history/audit log
- Advanced conflict resolution strategies
- Player change during active game (would require game model support)

---

## Document Version

- **Version**: 1.0
- **Date**: 2024
- **Status**: Specification Complete - Ready for Implementation

