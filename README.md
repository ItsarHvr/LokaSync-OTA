<header>
  <div align="center">

  <img src="frontend/public/lokasync_logo.png" width="200px" />

  <h1>LokaSync Web App</h1>

  <p>
    <img src="https://img.shields.io/badge/Version-1.0.1-green?style=flat-square" alt="lokasync-version" />
    <img src="https://img.shields.io/badge/Deployed%20on-Google%20Cloud%20VM-%234285F4.svg?style=flat-square&logo=google-cloud&logoColor=white" alt="google-cloud" />
  </p>

  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" />
    <img src="https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB" />
    <img src="https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white" />
    <img src="https://img.shields.io/badge/firebase-a08021?style=for-the-badge&logo=firebase&logoColor=ffcd34" />
    <img src="https://img.shields.io/badge/Google%20Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white" />
    <img src="https://img.shields.io/badge/EMQX-6966ff?style=for-the-badge&logo=mqtt&logoColor=white" />
  </p>

  </div>
</header>

---

## 👋 Introducing Our App

**What is LokaSync ?**

> LokaSync is a solution to make update firmware of your ESP devices more efficient, because it will update via Over-The-Air (OTA). Simply, our app is a **firmware version control** for your ESP devices.

**What happens if incorrect firmware is uploaded?**

> _It's your fault, not our team_. 🤭
> Traditionally, a mistake made during firmware flashing, such as setting incorrect configuration values, it **requires a manual re-flash of the ESP device**. This process is time-consuming and prone to error, especially for multiple devices deployed in various locations. So, it's crucial to **double check that firmware versions are verified** before an update is initiated.

**Why choose LokaSync?**

> _Because it's blazingly fast and secure_. ⚡
> LokaSync is built for **efficiency and security**. Firmware data is transmitted securely and with minimal bandwidth usage by leveraging the MQTT(S) protocol. 🚀
> User authentication is managed by Google through Firebase Authentication, ensuring that sensitive credentials are not handled or stored by our application.

## 🖥️ Development Environment

### 🏡 The FARM Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** — Used for backend API service.
- **[ReactJS](https://react.dev)** — Used for responsive frontend Single-Page Application (SPA).
- **[MongoDB](https://www.mongodb.com)** — Used as NoSQL database engine.

🔥 **Additional Tools and Libraries:**

- **[Vite](https://vite.dev)** — Frontend build tool and development server.
- **[TailwindCSS 4](https://tailwindcss.com/docs/installation/using-vite)** — Utility-first CSS framework.
- **[Shadcn/ui](https://ui.shadcn.com/docs)** — Composable and accessible UI components.
- **[reactbits-squares](https://www.reactbits.dev/backgrounds/squares)** — Animated background component.

### 🔐 Authentication System

Authentication is managed by Firebase Auth, providing a secure and reliable identity management system handled by Google.

### 🗂️ Cloud Storage

Firmware files are securely stored in the cloud using the Google Drive API. A service account key (JSON format) is required to authorize programmatic file uploads.

### 📡 Communication Protocol

The application utilizes the MQTT(S) protocol for firmware update and real-time communication. While EMQX Cloud is the recommended broker, any compatible MQTT broker (e.g., HiveMQ, Mosquitto) can be configured, provided it is accessible by all system components.

### 🐳 Containerized Deployment

The LokaSync application is containerized using Docker and orchestrated with Docker Compose. The environment consists of 4 main services:

- `mongo:8.0` — Provides the NoSQL database service.
- `python:3.13.3-alpine` — Runs the FastAPI backend application.
- `node:22.16.0-alpine` — Builds the static React frontend assets.
- `nginx:stable-alpine` — Serve web content from React buit files.
- `jc21/nginx-proxy-manager:latest` — Acts as reverse proxy.

## ✨ Features

| Description                                                                           | Status |
| ------------------------------------------------------------------------------------- | :----: |
| Over-the-Air (OTA) firmware updates for single devices (Cloud OTA)                    |   ✅   |
| Real-time logging of the firmware update process                                      |   ✅   |
| Log export functionality (PDF or CSV)                                                 |   ✅   |
| Automatic firmware storage on Google Drive                                            |   ✅   |
| Modern UI with a default dark theme                                                   |   ✅   |
| User profile customization                                                            |   ✅   |
| Easy deployment using `docker-compose.yml` file                                       |   ✅   |
| **Bonus**: Real-time sensor data monitoring (tested for `humidity` and `temperature`) |   ✅   |
| **In Progress**: Group OTA updates for multiple nodes                                 |   ⌛   |
| **In Progress**: Local OTA updates via ESP Access Point mode                          |   ⌛   |

## ℹ️ Usage

### 🔽 Clone the Repository (Not Published Yet / Private)

```shell
git clone https://github.com/LokaSync/LokaSync
cd LokaSync

# You can use this repo to clone
git clone https://github.com/ItsarHvr/LokaSync-OTA.git
# Then, change branch to `web-tmp`.
git fetch all
get checkout web-tmp
# Make sure you're in the branch
git branch --show-current
```

### 🗃️ Setup Google Drive API

![Google Drive API](./assets/images/gdrive-api.png)

- Navigate to the **[Google Cloud Console](https://console.cloud.google.com/)** and create a new project.
- Go to **APIs & Services** → **Enabled APIs & services**, search for and enable the **Google Drive API**.
- In the **Credentials** section, a new **Service Account** should be created. A name must be provided and the **Editor** role should be assigned to it.
- Within the new service account, navigate to the **Keys** tab and add a new key of type **JSON**.
- The JSON key file will be downloaded automatically. This file must be placed in the `backend/` folder.
- A new folder must be created in your personal Google Drive. This folder must then be shared with the email address that was generated for the service account. The **Editor** role should be granted to the service account during the sharing process.
- The ID for this new folder can be obtained from its URL. For example, if the URL is [https://drive.google.com/drive/folders/XXXXXX](https://drive.google.com/drive/folders/XXXXXX), the **Folder ID** is `XXXXXX`.
- Finally, the `GOOGLE_DRIVE_CREDS_NAME` (the name of your JSON file) and the `GOOGLE_DRIVE_FOLDER_ID` variables must be set in the backend's `.env` file.
- For a detailed walkthrough, this article may be helpful: [Python and Google Drive Tutorial](https://dev.to/binaryibex/python-and-google-drive-how-to-list-and-create-files-and-folders-2023-2nmm).

### 🔐 Create Firebase Authentication

![Firebase Auth](./assets/images/firebase-auth.png)

- Create a new project in the [Firebase Console](https://console.firebase.google.com/).
- Navigate to the **Authentication** section and enable the **Email/Password** sign-in method.
- From your Firebase project settings, **generate and download a new private key** (service account JSON file).
- Place the downloaded JSON file into the `backend/` folder.
- Set the `FIREBASE_CREDS_NAME` variable in the backend's `.env` file.
- Copy the web app configuration details from Firebase and populate the corresponding `VITE_FIREBASE_*` variables in the frontend's `.env` file.

### 📡 Setup MQTT Broker

![EMQX Dashboard](./assets/images/mqtt-broker-dashboard.png)

- An MQTT broker is required. A free-tier instance from [EMQX Cloud](https://www.emqx.com/en/cloud) can be used, or you may deploy a local broker.
- Once the broker is running, configure the connection details in the `.env` files for both the backend and frontend, including the broker username and password.
- If MQTTS is used, the broker's CA certificate file must be placed in the `backend/` folder and its path specified in the configuration. The frontend does not require this certificate file for WebSocket connections.

### ⚙️ Configure Backend `.env` File

Create a `.env` file in the `backend/` folder and populate it with the following:

```txt
# Database Configuration
MONGO_USERNAME=mongo_admin
MONGO_PASSWORD=mongo_password
MONGO_HOST=mongodb # Change this if you're using MongoDB in host machine
MONGO_PORT=27017 # Change this if you're use MongoDB in host machine
MONGO_DATABASE_NAME=app_db

# MQTT Configuration
MQTT_BROKER_URL=broker.emqx.io
MQTT_BROKER_PORT=1883

# Firebase Configuration
FIREBASE_CREDS_NAME=firebase-credentials.json

# Google Drive Configuration
GOOGLE_DRIVE_CREDS_NAME=gdrive-credentials.json
GOOGLE_DRIVE_FOLDER_ID=REDACTED

# Default Backend Timezone
# Adjust timezone according to your location
# e.g. Asia/Tokyo
TIMEZONE=Asia/Jakarta
```

### ⚙️ Configure Frontend `.env` File

Create a `.env` file in the `frontend/` folder and populate it with the following:

```txt
# Firebase Auth related configuration
VITE_FIREBASE_API_KEY=REDACTED
VITE_FIREBASE_AUTH_DOMAIN=REDACTED
VITE_FIREBASE_PROJECT_ID=REDACTED
VITE_FIREBASE_STORAGE_BUCKET=REDACTED
VITE_FIREBASE_MESSAGING_SENDER_ID=REDACTED
VITE_FIREBASE_APP_ID=REDACTED

# API related configuration
# Note: Avoid using docker compose service name like `http://backend`.
VITE_BASE_API_URL=http://localhost:8000

# MQTT related configuration
VITE_MQTT_BROKER_URL=ws://broker.emqx.io:8083/mqtt
```

### ️️⚙️ Configure Docker Compose `.env` File

Create a `.env` file in the root folder and populate with the following:

```txt
# Database Configuration
MONGO_USERNAME=mongo_admin
MONGO_PASSWORD=mongo_password
MONGO_DATABASE=app_db
MONGO_PORT=27017 # Change this if you're not using the default MongoDB port.

# External Services Configuration
GOOGLE_DRIVE_CREDS_NAME=gdrive-credentials.json
FIREBASE_CREDS_NAME=firebase-credentials.json
MQTTS_BROKER_CERT_NAME=emqxsl-ca.crt

# Backend Configuration
BACKEND_PORT=8000
# Backend will running on port 8000

# Frontend Configuration
FRONTEND_PORT=3000
# Frontend will running on port 3000
```

> ⚠️ **Important**: Please refer to the `.env.example` fie and ensure all env variables are set correctly before proceeding.

## 🚀 Run the App with Docker Compose

```shell
# This command will build the images and start all services in detached mode.
docker-compose up -d

# On some Linux distributions, sudo may be required.
sudo docker-compose up -d
```

## ▶️ Demo Video

🎥 _Coming Soon_.

## ⚔️ LokaSync Team

| Name                      | Student ID (NIM) | Roles                               |
| ------------------------- | ---------------- | ----------------------------------- |
| Alfarizki Nurachman       | 2207421041       | Back-end Developer                  |
| Itsar Hevara              | 2207421046       | Team Manager + IoT Developer        |
| Jonathan Victorian Wijaya | 2207421051       | IoT Developer                       |
| Wahyu Priambodo           | 2207421048       | Web Pentester + SysAdmin + Front-end Developer |

## 📬 Contact

- LokaSync Team: [Itsar Hevara](mailto:itsar.hevara.tik22@mhsw.pnj.ac.id)
- Lokatani: [Official contact](https://lokatani.id/contact-us)

---

<footer style="display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; padding: 1em 0;">
  <span>&copy; 2025 - LokaSync</span>
  <span>Supported by PNJ and Lokatani.</span>
</footer>
