# Intentra Project Specification

## Computer Control System Using Gaze Tracking and Hand Gestures

**Version:** 1.0\
**Date:** November 9, 2026\
**Status:** Initial complete specification based on the decisions made

------------------------------------------------------------------------

## 1. Project Overview

Intentra is a system that allows users to control a computer using gaze
tracking and hand gestures, without relying on a physical mouse for
everyday interaction.

The system consists of a Desktop application installed on the computer,
a Web application for managing user settings, and a central Backend
server. The Desktop application performs the actual computer-control
operations and can receive settings and software updates from the
server.

In Phase 1, the system will detect the user's gaze position and hand
gestures. In Phase 2, voice-command support will be added.

## 2. Goals and Responsibilities

### 2.1 Supported Control Actions in Phase 1

The system will support only the following five actions:

1.  Move the mouse cursor.
2.  Single click.
3.  Double-click.
4.  Right-click.
5.  Scrolling --- precise scrolling and fast scrolling.

All actions must work in web browsers as well as ordinary desktop
applications installed on the computer. Control will be performed at the
operating-system level, rather than through a browser-specific
mechanism.

### 2.2 Component Responsibilities

  ---------------------------------------------------------------------
  Component                          Responsibility
  ---------------------------------- ----------------------------------
  Desktop Application                Detect gaze and gestures, process
                                     them, and execute mouse actions on
                                     the computer

  Web Client                         User registration, login,
                                     switching between users, and
                                     settings management

  Backend                            Authentication, user and settings
                                     management, storage, and delivery
                                     of updates

  MongoDB                            Store user data, settings, and
                                     required information

  Update Mechanism                   Deliver settings and software
                                     updates to the Desktop application
  ---------------------------------------------------------------------

## 3. Overall Architecture

The system will be divided into three separate applications:

### 3.1 Desktop Application

-   **Language:** Python.
-   **Target operating system:** Windows.
-   **Purpose:** Detect visual input and execute mouse actions.
-   The application may run in the background, according to the user's
    settings.
-   The application will identify the current operating-system user and
    load the settings associated with that user from the server.
-   The application will be able to receive settings updates and
    software-version updates from the server.

### 3.2 Web Application

-   **Technologies:** React and TypeScript.
-   **Local development address:** `http://localhost:3000`.
-   **Purpose:** User interface for account and settings management.
-   Users will be able to register, log in, log out, and switch between
    accounts.
-   Users will be able to change settings and save them to the server.
-   The Web application will not perform mouse actions on the computer.
    Those actions will be performed by the Desktop application.

### 3.3 Backend Server

-   **Language:** Python.
-   **Framework:** FastAPI.
-   **Development port:** `8000`.
-   **Purpose:** Central API for the Web application and the Desktop
    application.
-   The server will handle authentication, authorization, settings
    storage and retrieval, version information, and updates.

### 3.4 Database

-   **Database:** MongoDB.
-   It will store users, securely stored login information, user
    settings, user-to-computer associations, and version/update
    information.
-   Passwords must not be stored as readable text. They must be stored
    as hashes generated using an appropriate, established
    password-hashing algorithm.

## 4. Technologies and Libraries

### 4.1 Desktop --- Python

  -----------------------------------------------------------------------
  Area                    Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Programming language    Python                  Implement the Desktop
                                                  application

  Image processing        OpenCV                  Camera capture, frame
                                                  acquisition, and image
                                                  processing

  Face and                MediaPipe Face          Detect facial landmarks
  facial-landmark         Landmarker              and eye regions
  detection

  Hand detection          MediaPipe Hand          Detect the hand
                          Landmarker              skeleton, fingers, and
                                                  joint landmarks

  Mouse control           PyAutoGUI               Move the cursor, click,
                                                  and scroll

  System-event listening  Pynput                  Monitor mouse and
                                                  keyboard events when
                                                  needed

  Windows integration     PyWin32                 Window detection and
                                                  operating-system
                                                  integration

  Desktop UI              PySide6                 Settings window, system
                                                  status, calibration,
                                                  and notifications

  HTTP communication      HTTPX or Requests       Communicate with
                                                  FastAPI

  Local storage           SQLite                  Store cached settings
                                                  and local state that
                                                  does not conflict with
                                                  server settings
  -----------------------------------------------------------------------

**Implementation note:** PyAutoGUI will be the primary component for
executing mouse actions. Pynput will be used to listen for system events
where monitoring is required; two competing mechanisms will not be
created to execute the same action. PyWin32 will be used for
Windows-specific functionality that is not adequately covered by the
general mouse-control layer.

### 4.2 Web Client --- React and TypeScript

  ---------------------------------------------------------------------
  Technology                         Purpose
  ---------------------------------- ----------------------------------
  React                              Build the user interface

  TypeScript                         Define types and models and
                                     perform development-time type
                                     checking

  React Router                       Navigate between screens

  State-management library           Manage authentication and settings
                                     state

  Fetch or Axios                     Send API requests to the server

  Build tool such as Vite            Run and build the Web application
  ---------------------------------------------------------------------

The specific state-management and UI libraries will be selected during
implementation. The architecture does not depend on a particular
library.

### 4.3 Backend --- Python and FastAPI

  ---------------------------------------------------------------------
  Technology                         Purpose
  ---------------------------------- ----------------------------------
  Python                             Server-side programming language

  FastAPI                            Expose the API

  Pydantic                           Validate requests and responses

  PyMongo or Motor                   Access MongoDB, depending on the
                                     selected execution model

  JWT or a secure Session mechanism  Manage user authentication

  Argon2 or bcrypt                   Hash passwords

  HTTPS                              Encrypt communication in
                                     Production
  ---------------------------------------------------------------------

### 4.4 Infrastructure

-   **MongoDB** --- the database.
-   **Docker** --- run the server and database services in suitable
    development or deployment environments.
-   **Git** --- source-code version control.
-   **`.env` files** --- store environment configuration and secrets;
    secrets must not be embedded in source code.
-   **Logging system** --- record errors and operational events without
    unnecessarily storing personal information or camera images.

The Desktop application will be installed and run as a regular Windows
application. It must not run inside Docker because it requires direct
access to the camera and the operating system's mouse interface.

## 5. Proposed Project Directory Structure

The project will use a Monorepo structure containing three separate
application directories and documentation:

``` text
intentra/
│
├── desktop/
│   ├── src/
│   │   ├── main.py
│   │   ├── app/
│   │   │   ├── application.py
│   │   │   ├── lifecycle.py
│   │   │   └── configuration.py
│   │   │
│   │   ├── vision/
│   │   │   ├── camera.py
│   │   │   ├── face_tracker.py
│   │   │   ├── gaze_estimator.py
│   │   │   ├── hand_tracker.py
│   │   │   ├── calibration.py
│   │   │   └── frame_pipeline.py
│   │   │
│   │   ├── gestures/
│   │   │   ├── gesture_detector.py
│   │   │   ├── pinch_detector.py
│   │   │   ├── gesture_state.py
│   │   │   └── gesture_config.py
│   │   │
│   │   ├── scrolling/
│   │   │   ├── precise_scroll.py
│   │   │   ├── fast_scroll.py
│   │   │   └── scroll_classifier.py
│   │   │
│   │   ├── actions/
│   │   │   ├── base_action.py
│   │   │   ├── move_cursor.py
│   │   │   ├── left_click.py
│   │   │   ├── double_click.py
│   │   │   ├── right_click.py
│   │   │   ├── scroll_action.py
│   │   │   ├── action_registry.py
│   │   │   └── action_dispatcher.py
│   │   │
│   │   ├── input_control/
│   │   │   ├── mouse_controller.py
│   │   │   ├── system_listener.py
│   │   │   └── windows_controller.py
│   │   │
│   │   ├── user/
│   │   │   ├── os_user_identity.py
│   │   │   ├── device_identity.py
│   │   │   └── user_settings.py
│   │   │
│   │   ├── services/
│   │   │   ├── api_client.py
│   │   │   ├── settings_sync.py
│   │   │   ├── update_service.py
│   │   │   └── connectivity.py
│   │   │
│   │   ├── storage/
│   │   │   ├── local_database.py
│   │   │   └── settings_cache.py
│   │   │
│   │   └── ui/
│   │       ├── main_window.py
│   │       ├── settings_window.py
│   │       ├── calibration_window.py
│   │       └── status_indicator.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── web/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── auth.ts
│   │   │   └── settings.ts
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   └── DevicesPage.tsx
│   │   ├── features/
│   │   │   ├── account/
│   │   │   ├── gaze/
│   │   │   ├── gestures/
│   │   │   └── updates/
│   │   ├── types/
│   │   └── hooks/
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── server/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── dependencies.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── settings.py
│   │   │   │   ├── devices.py
│   │   │   │   └── updates.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── settings_service.py
│   │   │   ├── device_service.py
│   │   │   └── update_service.py
│   │   ├── repositories/
│   │   │   └── mongo_repository.py
│   │   └── database/
│   │       └── mongo.py
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── shared/
│   ├── api-contracts/
│   └── documentation/
│
├── infrastructure/
│   ├── docker-compose.yml
│   ├── Dockerfile.server
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── gestures.md
│   └── installation.md
│
└── README.md
```

This is a proposed logical structure. Files may be split or combined
during implementation, but the separation between detection, action
decision-making, action execution, and server communication must be
maintained.

## 6. Desktop Application --- Detailed Description

### 6.1 Application Startup

When the application starts:

1.  Load local settings.
2.  Identify the current Windows user.
3.  Identify the computer or application installation.
4.  Connect to the FastAPI server.
5.  Retrieve the relevant user settings.
6.  Check camera availability.
7.  Load the face- and hand-detection models.
8.  Start the gaze- and gesture-detection pipeline.
9.  Display the application status in the interface.

If the server is unavailable, the application may use the most recently
saved local settings, if available. Settings changes made while offline
will be marked as pending synchronization, according to the policy
defined during implementation.

### 6.2 Gaze Tracking

**Goal:** The user's gaze position will control the mouse cursor.

Components: - OpenCV for camera-frame capture. - MediaPipe Face
Landmarker for detecting facial landmarks and eye regions. - Gaze
Estimator for calculating the gaze direction. - Calibration for adapting
the system to the user's facial structure, camera position, and screen.

Process:

1.  Receive frames from the camera.
2.  Detect the face and relevant landmarks.
3.  Estimate the gaze direction.
4.  Convert the gaze estimate into screen coordinates.
5.  Smooth cursor movement to reduce jitter.
6.  Send the coordinates to the Mouse Controller.

The system will include a calibration stage in which the user is asked
to look at several points on the screen. The calibration data will be
used to map gaze to screen coordinates.

**Accuracy note:** MediaPipe provides facial and eye landmarks, but does
not by itself guarantee gaze-tracking accuracy comparable to a dedicated
commercial eye-tracking product. Therefore, the Gaze Estimator component
and individual calibration are essential. Accuracy must be tested on the
target hardware.

### 6.3 Hand-Gesture Detection

**Goal:** Detect hand gestures and convert them into mouse commands.

Components: - OpenCV for image capture. - MediaPipe Hand Landmarker for
detecting hand landmarks. - Gesture Detector for identifying pinches,
pinch duration, and hand movement. - Gesture State for managing gesture
states and preventing duplicate activation.

The system will detect at least: - Thumb-tip position. -
Index-finger-tip position. - Distance between the fingertips. - Whether
the pinch is open or closed. - Pinch duration. - Hand movement over
time. - Wrist-movement speed and direction.

### 6.4 Gesture-to-Action Mapping

The approved mapping is:

  ---------------------------------------------------------------------
  Action                             Gesture
  ---------------------------------- ----------------------------------
  Single click                       Briefly pinch the thumb and index
                                     finger together, then release

  Double-click                       Perform two quick pinches in
                                     succession

  Right-click                        Hold the thumb-and-index-finger
                                     pinch without significant hand
                                     movement

  Precise scrolling                  Pinch the thumb and index finger
                                     together and gradually move the
                                     hand up or down

  Fast scrolling                     Pinch the same fingers, make a
                                     quick wrist movement up or down,
                                     and then release
  ---------------------------------------------------------------------

The mouse cursor will be moved using gaze position, not hand gestures.

### 6.5 Precise Scrolling

Operating principle:

1.  The user brings the thumb and index finger together.
2.  The system detects that the pinch is being held.
3.  The user gradually moves the hand upward or downward.
4.  The system measures the hand movement over time.
5.  The hand movement is converted into continuous scrolling.
6.  Scrolling stops when the user releases the pinch.

Scrolling will correspond to the hand's movement rather than relying
only on a fixed scrolling speed.

Required parameters: - Pinch-detection threshold. - Minimum movement
required to activate scrolling. - Conversion ratio between hand movement
and scroll amount. - Movement smoothing. - Jitter threshold. - Maximum
scrolling speed.

### 6.6 Fast Scrolling

Operating principle:

1.  The user brings the thumb and index finger together.
2.  The user makes a quick wrist movement upward or downward.
3.  The system measures the movement's direction, speed, and intensity.
4.  The user releases the pinch.
5.  The system performs fast scrolling according to the direction and
    intensity of the movement.

Required parameters: - Minimum speed for detecting a fast movement. -
Acceleration threshold. - Movement direction. - Scrolling intensity. -
Scrolling duration or deceleration profile. - Noise threshold to prevent
unintended activation.

### 6.7 Preventing Gesture Conflicts

Right-clicking and scrolling both use a pinch of the same fingers.
Therefore, a gesture-classification mechanism based on pinch duration
and hand movement is required.

Rules: - Short pinch followed by release: single click. - Two short
pinches within a defined time interval: double-click. - Long pinch
without significant movement: right-click. - Long pinch with gradual
movement: precise scrolling. - Pinch with fast movement: fast scrolling,
activated when the pinch is released.

Time and movement thresholds must be defined through experiments and
calibration. Final numeric values must not be selected before testing
with the camera, users, and target hardware.

The gesture mechanism will manage explicit states, for example: - `IDLE`
--- no active gesture. - `PINCH_DETECTED` --- a pinch has been
detected. - `SHORT_PINCH` --- a short pinch. - `HOLDING` --- a sustained
pinch. - `PRECISE_SCROLL` --- gradual movement detected. -
`FAST_SCROLL_CANDIDATE` --- fast movement detected. - `RELEASED` ---
pinch released and final classification performed. - `COOLDOWN` ---
short delay to prevent duplicate detection.

A single gesture must never trigger more than one action. For example, a
pinch initially classified as a possible fast-scroll gesture must not
also trigger a right-click.

## 7. Mouse-Action Execution Layer

### 7.1 Principle

All actions will be executed through an OS-level control layer. This
means that the system sends mouse events to the operating system,
allowing the actions to work in both browsers and ordinary desktop
applications, subject to Windows permissions and limitations.

### 7.2 Actions

  Action                                         Implementation
  ---------------------------------------------- ----------------------
  Move mouse                                     PyAutoGUI
  Single click                                   PyAutoGUI
  Double-click                                   PyAutoGUI
  Right-click                                    PyAutoGUI
  Scroll                                         PyAutoGUI
  Detect active window and Windows information   PyWin32, when needed
  Listen for system events                       Pynput, when needed

### 7.3 Separation Between Detection and Execution

The gesture-detection component will not directly execute mouse clicks.
Instead, it will produce an internal event, such as `RIGHT_CLICK` or
`PRECISE_SCROLL`.

The event will pass through:

1.  Gesture Detector.
2.  Action Dispatcher.
3.  Action Registry.
4.  The relevant Action.
5.  Mouse Controller.
6.  The operating system.

This separation will make it possible to add future actions without
changing the camera-detection mechanism or the operating-system input
mechanism.

### 7.4 Common Action Interface

Each action will implement a common interface, for example:

``` python
class BaseAction:
    def execute(self, context):
        raise NotImplementedError
```

Each action will be an independent module. The Action Registry will
register the available actions, and the Action Dispatcher will route
each event to the appropriate action.

## 8. Desktop User Interface

The interface will be built using PySide6 and will include:

-   Application status: active, paused, or unavailable.
-   Camera status.
-   Face-detection status.
-   Hand-detection status.
-   Gaze-calibration status.
-   Display of the associated user or settings account.
-   Server-connection status.
-   Update checking.
-   An option to enable or pause control.
-   Access to a basic local settings screen.

The local interface will not replace the Web application for full
settings management.

## 9. Web Application

### 9.1 Purpose

The Web application will be used to manage the user's account and
personal settings. It will not control the mouse and will not perform
gaze tracking or gesture detection.

### 9.2 Screens

**Registration Screen** - Create an account. - Enter login details. -
Validate the submitted data.

**Login Screen** - Log in using a username and password. - Receive an
authentication token. - Navigate to the user's personal area.

**Dashboard** - Display account status. - Display associated computers,
if any. - Display the last settings-synchronization time.

**Settings Screen** - Gaze-tracking settings. - Cursor smoothing and
sensitivity settings. - Pinch-detection threshold. - Double-click
settings. - Right-click settings. - Precise-scrolling settings. -
Fast-scrolling settings. - Save changes to the server.

**Account Management Screen** - Log out. - Switch between users. -
Manage account details according to the features implemented.

**Computers/Devices Screen** - Display Desktop installations associated
with the user. - Display synchronization status. - Display the
application version.

## 10. User Management and Identity in the Desktop Application

### 10.1 Web Application

The website will allow users to: - Register. - Log in. - Log out. -
Switch between accounts. - Manage settings for the currently logged-in
account.

### 10.2 Desktop Application

In the Desktop application, the user is determined by the currently
active operating-system user (`USER`).

When the application starts:

1.  The application identifies the current Windows account.
2.  The application identifies the computer installation.
3.  The application requests from the server the settings associated
    with that identity.
4.  The application loads the settings and starts the system.

A local Windows username must not be assumed to be a globally unique
identifier by itself. Reliable association with server data requires a
more stable identifier, such as the operating-system user identifier
together with an installation/computer identifier, as well as a
registration or association mechanism linked to a Web account.

## 11. Backend --- API

### 11.1 Responsibilities

-   Registration and login.
-   Authentication and authorization.
-   User management.
-   Saving and retrieving settings.
-   Registering computers and Desktop installations.
-   Associating settings with a user or device.
-   Checking versions and updates.
-   Returning data in a consistent format.

### 11.2 Proposed API Endpoints

The following endpoints are proposed for the server interface:

  -----------------------------------------------------------------------------
  Method              Endpoint                              Purpose
  ------------------- ------------------------------------- -------------------
  POST                `/api/auth/register`                  Register a user

  POST                `/api/auth/login`                     Log in

  POST                `/api/auth/logout`                    Log out or
                                                            invalidate a
                                                            session

  GET                 `/api/users/me`                       Retrieve the
                                                            currently
                                                            authenticated user

  GET                 `/api/settings`                       Retrieve settings

  PUT                 `/api/settings`                       Update settings

  POST                `/api/devices/register`               Register a Desktop
                                                            installation

  GET                 `/api/devices`                        List associated
                                                            devices

  GET                 `/api/devices/{device_id}/settings`   Retrieve settings
                                                            for a device

  GET                 `/api/updates/check`                  Check for an update

  GET                 `/api/updates/latest`                 Retrieve the latest
                                                            version information
  -----------------------------------------------------------------------------

Every endpoint will include appropriate authorization checks. Endpoints
that require an authenticated user must not be publicly accessible.

### 11.3 Ports

-   Web Client: `3000`.
-   FastAPI Server: `8000`.
-   MongoDB: default port `27017` in a local development environment
    only, unless configured otherwise.

In Production, secure addresses and network configuration must be used.
MongoDB must not be exposed directly to the internet.

## 12. MongoDB Data Structure

The following is a proposed logical structure.

### 12.1 Users

``` json
{
  "_id": "user_id",
  "username": "example",
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 12.2 Settings

``` json
{
  "_id": "settings_id",
  "user_id": "user_id",
  "gaze": {
    "smoothing": 0.5,
    "sensitivity": 1.0,
    "calibration_data": {}
  },
  "gestures": {
    "pinch_threshold": 0.0,
    "short_pinch_max_duration_ms": 0,
    "double_click_interval_ms": 0,
    "right_click_hold_ms": 0,
    "movement_threshold": 0.0
  },
  "scroll": {
    "precise_sensitivity": 1.0,
    "fast_scroll_threshold": 0.0,
    "fast_scroll_intensity": 1.0
  },
  "updated_at": "timestamp",
  "version": 1
}
```

The numeric values in this example are placeholders only. Actual values
must be determined through testing and calibration.

### 12.3 Devices

``` json
{
  "_id": "device_id",
  "user_id": "user_id",
  "os_user_identifier": "local_os_user_identifier",
  "installation_id": "installation_id",
  "device_name": "computer_name",
  "desktop_version": "1.0.0",
  "last_seen": "timestamp",
  "created_at": "timestamp"
}
```

### 12.4 Updates

``` json
{
  "_id": "release_id",
  "version": "1.0.0",
  "platform": "windows",
  "download_url": "release_download_location",
  "release_notes": "description",
  "published_at": "timestamp",
  "minimum_supported_version": "1.0.0"
}
```

## 13. Settings Synchronization and Updates

### 13.1 Settings Synchronization

1.  The user changes a setting on the website.
2.  React sends a PUT request to FastAPI.
3.  FastAPI authenticates the user and validates the data.
4.  The server saves the settings in MongoDB.
5.  The Desktop application checks whether a newer settings version
    exists.
6.  The application downloads the settings and updates its local
    configuration.

The synchronization mechanism may use periodic polling or a Push
mechanism. The mechanism will be selected during implementation. The
application does not need to reload all data if nothing has changed.

### 13.2 Settings Versions

Each settings document will have a version number or an `updated_at`
timestamp. The Desktop application will compare its local version with
the server version and download the data only when a change exists.

### 13.3 Software Updates

The following must be treated separately: - User-settings updates. -
Desktop application version updates.

The update server will provide information about the available version,
compatibility, download link, and release notes. The installation
mechanism must verify the integrity and signature of an update package
before installation. Updates must not be installed from an unverified
file or URL.

## 14. Security and Privacy

-   All Production communication will use HTTPS.
-   Passwords will be stored as strong hashes, not as plain text.
-   Access tokens will be stored securely.
-   API permissions will be checked on the server.
-   A user must not be able to read or modify another user's settings.
-   Device identifiers must not be used as a substitute for
    authentication.
-   Access to MongoDB must be restricted.
-   Secrets must be protected using environment variables or a secrets
    manager.
-   Storage of visual data must be minimized. Camera images and frames
    will not be sent to the server during normal operation unless a
    separate, explicit requirement is defined.
-   The user must receive a clear indication whenever the camera is
    active and whenever mouse control is active.
-   The system must allow control to be paused immediately.

## 15. Phase 2 --- Voice Commands

This phase will be developed after Phase 1 has been completed and
tested.

Its purpose is to add the ability to control the system using voice
commands. The component will include: - Capturing audio from the
microphone. - Speech recognition. - Converting speech into an internal
command. - Sending the command to the Action Dispatcher. - Executing the
action through the existing control layer.

The specific speech-recognition technology, such as Vosk or an
alternative, will be selected when this phase begins. Voice recognition
is not required in Phase 1.

## 16. Recommended Development Sequence

### Step 1 --- Project Infrastructure

-   Create the Monorepo structure.
-   Set up the Python environment.
-   Create the React + TypeScript application.
-   Set up FastAPI.
-   Connect MongoDB.
-   Configure environment variables and Logging.

### Step 2 --- Mouse-Control Layer

-   Implement the Mouse Controller.
-   Implement cursor movement, single-click, double-click, right-click,
    and scrolling.
-   Test in a browser.
-   Test in ordinary Desktop applications.

### Step 3 --- Hand and Gesture Detection

-   Connect the camera.
-   Detect hands using MediaPipe.
-   Detect pinches.
-   Implement the gesture state machine.
-   Implement the five actions according to the approved mapping.
-   Test to prevent incorrect gesture detection.

### Step 4 --- Gaze Tracking

-   Detect the face and eyes.
-   Implement calibration.
-   Map gaze to screen coordinates.
-   Smooth movement.
-   Connect gaze tracking to cursor movement.

### Step 5 --- Desktop Interface

-   Build the PySide6 interface.
-   Add a calibration screen.
-   Add active and paused states.
-   Display camera, detection, and server-connection status.

### Step 6 --- Web and Accounts

-   Implement registration and login.
-   Manage sessions.
-   Build settings screens.
-   Save settings on the server.
-   Implement account switching and logout.

### Step 7 --- Desktop Association and Synchronization

-   Identify the Windows user.
-   Register the installation/computer.
-   Complete the association mechanism with the Web account.
-   Load settings from the server.
-   Synchronize changes.

### Step 8 --- Updates

-   Check the application version.
-   Download a verified update.
-   Install and apply the update.
-   Test compatibility and the ability to roll back to a previous
    version, if implemented.

### Step 9 --- System Testing

-   Unit tests.
-   Integration tests.
-   Long-duration usage tests.
-   Compatibility tests in browsers and Desktop applications.
-   Performance, accuracy, and stability tests.

### Step 10 --- Phase 2: Voice

-   Capture audio.
-   Recognize commands.
-   Map commands to actions.
-   Integrate with the Action Dispatcher.

## 17. Testing and Acceptance Criteria

The system will be considered ready for Phase 1 when the following
criteria are met:

### Gaze Tracking

-   The user can calibrate the system.
-   Gaze moves the cursor.
-   Cursor movement is sufficiently stable for practical use.
-   Control can be paused and resumed.

### Gesture Detection

-   A short pinch triggers exactly one single-click.
-   Two quick pinches trigger exactly one double-click.
-   A sustained pinch without significant movement triggers a
    right-click.
-   A pinch with gradual movement triggers precise scrolling.
-   A pinch with fast movement followed by release triggers fast
    scrolling.
-   A single gesture does not accidentally trigger two actions.

### Application Compatibility

-   All five actions are tested in a browser.
-   All five actions are tested in several ordinary Desktop
    applications.
-   Mouse actions are sent to the operating system and do not depend on
    the structure of a particular website.

### Users and Settings

-   A user can register and log in on the website.
-   A user can switch between accounts on the website.
-   A user can save settings.
-   The Desktop application identifies the current Windows user.
-   The application loads the settings associated with the identity
    configured for it.
-   Settings changes made on the website reach the Desktop application.

### Updates

-   The application detects when an update is available.
-   The application checks compatibility and integrity before
    installation.
-   A failed update does not leave the application unusable.

Additional Functional Requirements
### 1. Screen Support
In Phase 1, Intentra will support a single monitor only. Multi-monitor support is out of scope for the initial release.

### 2. User Identification and Computer Association
- A single Intentra user account can be connected to multiple computers.
- The Desktop application identifies the user through their Intentra account.
- The application also associates the currently signed-in Windows user with the corresponding Intentra account.
- This association allows the application to recognize the configured user on subsequent launches.
- User and computer associations must be maintained consistently.

### 3. Manual Application Launch
- Intentra Desktop must not launch automatically when Windows starts.
- The user is responsible for launching the application manually.
- The application should operate only when the user chooses to activate it.

### 4. Gaze Calibration Persistence
- The gaze calibration results must be saved and retained between application sessions.
- The application should reuse the saved calibration when launched again, without requiring the user to repeat the calibration process.
- Calibration data should be associated with the relevant computer and user, rather than assumed to be identical across all computers.

### 5. Gesture Mapping
- The gesture mapping defined in the current specification is the approved mapping for Phase 1.
- No changes should be made to the existing gesture-to-action mapping during initial development.
- Future versions may allow users to customize gesture mappings, but this capability is out of scope for Phase 1.
-
## 18. Summary

Intentra will be built as a system with three independent components:

-   A Python Desktop application that detects gaze and hand gestures and
    controls the mouse at the operating-system level.
-   A React and TypeScript Web application for user and settings
    management.
-   A Python server using FastAPI and MongoDB for managing accounts,
    settings, devices, and updates.

In Phase 1, the system will support cursor movement through gaze
tracking, single-click, double-click, right-click, precise scrolling,
and fast scrolling through hand gestures. In Phase 2, control through
voice commands will be added.

The architecture will remain modular: input detection, gesture
interpretation, action selection, and action execution will be separate
components. This will make it possible to add future capabilities
without rewriting the core mechanisms.
