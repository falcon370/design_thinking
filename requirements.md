
# 📌 Campus Crowd Awareness System

## Version 1.0 – Updated Requirements (Final)

---

## 1️⃣ Problem Statement

Students and staff move between campus locations without awareness of current crowd conditions, leading to congestion, delays, and safety risks during peak hours.

---

## 2️⃣ Goal (Version 1.0)

> Provide real-time and short-term crowd awareness for a campus location using a camera-based system that is demonstrable, privacy-preserving, and production-aligned.

---

## 3️⃣ Scope (Explicitly Locked for V1.0)

### Included

* Single monitored location
* Single elevated camera
* Real-time crowd density estimation
* Short-term trend awareness
* Web-based visualization
* Limited user access

### Excluded

* Identity recognition
* Attendance tracking
* Campus-wide deployment
* Multi-sensor fusion
* Long-term prediction

---

## 4️⃣ System Context (V1.0 Deployment Assumption)

* A **Wi-Fi IP camera** is installed at an elevated, fixed position.
* A **single laptop** hosts:

  * Edge Analytics Service
  * Crowd Service
  * Presentation Service (Web)
* Users access the system via a **web browser** (desktop or mobile).

> Logical separation is maintained even though services are co-located.

---

## 5️⃣ Functional Requirements (V1.0)

### FR-1: Live Video Input

* The system shall receive a live video stream from a fixed camera.
* The camera shall monitor a public campus area only.

---

### FR-2: Person Detection

* The system shall detect people present in the camera view.
* Detection shall be anonymous and non-identifying.

---

### FR-3: Crowd Count Estimation

* The system shall estimate the number of people in the monitored area.
* Exact accuracy is not mandatory; approximate counts are acceptable.

---

### FR-4: Crowd Density Classification

* The system shall classify crowd levels into:

  * Low
  * Medium
  * High
  * Critical
* Thresholds shall be configurable.

---

### FR-5: Real-Time Updates

* Crowd status shall update continuously at regular intervals.
* Visible changes in crowd size shall reflect during live operation.

---

### FR-6: Short-Term Trend Awareness

* The system shall indicate short-term crowd trends as:

  * Increasing
  * Stable
  * Decreasing
* Trend analysis shall be based on recent observations only.

---

### FR-7: Threshold-Based Alerts

* The system shall generate alerts when:

  * Crowd density crosses a predefined threshold
  * Sudden abnormal increases are detected
* Alerts shall be visual (color / text).

---

### FR-8: Web-Based Visualization

* The system shall present crowd information via a web dashboard.
* The dashboard shall display:

  * Location name
  * Crowd density level (color-coded)
  * Trend indicator
  * Alert status
  * Last update time

---

### FR-9: Limited User Access

* The system shall support view-only access for a limited set of users.
* Users shall not have access to video feeds.

---

## 6️⃣ Technical Design Requirements (Demo-Specific)

### TR-1: Edge Analytics Service

* Shall run on a laptop.
* Shall connect to the camera via Wi-Fi.
* Shall process video frames locally.
* Shall output only numerical metadata.

---

### TR-2: Crowd Service

* Shall run on the same laptop.
* Shall receive metadata from the edge service.
* Shall maintain the latest crowd state.
* Shall expose data via an internal API.

---

### TR-3: Presentation Service

* Shall run on the same laptop.
* Shall fetch data from the crowd service.
* Shall serve a responsive web interface usable on mobile and desktop browsers.

---

### TR-4: Data Isolation

* Raw video shall not be stored.
* Video frames shall not be exposed beyond the edge service.
* Only aggregated metadata shall be shared.

---

## 7️⃣ Non-Functional Requirements (V1.0)

### NFR-1: Latency

* System updates should feel near real-time (≤ 10 seconds).

### NFR-2: Privacy

* No face recognition.
* No identity tracking.
* No personal data storage.

### NFR-3: Reliability

* The system shall handle:

  * Moderate lighting variation
  * Partial occlusion
  * Continuous movement

### NFR-4: Usability

* Users shall understand crowd status within 3 seconds of viewing the dashboard.

---

## 8️⃣ Constraints (Declared Intentionally)

* Single camera
* Single location
* Fixed camera angle
* Laptop-based processing
* Prototype-level accuracy

> These constraints are intentional to ensure demo reliability.

---

## 9️⃣ Success Criteria (V1.0)

* Crowd level visibly changes with real movement
* Dashboard updates in real time
* Users can make simple movement decisions
* No privacy concerns raised
* System runs continuously during demo

---

## 🔑 One-Line Version 1.0 Summary (Memorize)

> “Version 1.0 is a camera-based, privacy-preserving crowd awareness system that provides real-time density and short-term trend insights using edge analytics and a web dashboard.”

