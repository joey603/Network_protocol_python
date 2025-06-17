# Network Communication Projects

This repository contains three distinct Python network communication projects, each demonstrating different aspects of TCP socket programming and distributed systems.

## Projects Overview

### 1. P2P TCP Messaging System (`p2p tcp/`)
A peer-to-peer messaging system with distributed servers that can relay messages between users across different server instances.

**Features:**
- Multi-server architecture with automatic server discovery
- User-to-user messaging with message forwarding
- Duplicate message detection using UUIDs
- Real-time message delivery
- Thread-safe client and server connections

### 2. RTT-Optimized Messaging (`RTT/`)
An intelligent messaging system that automatically selects the best server based on Round Trip Time (RTT) measurements.

**Features:**
- Automatic RTT measurement to all available servers
- Smart server selection (connects to the fastest server)
- Seamless server switching
- User messaging with optimal latency
- Performance monitoring

### 3. Basic TCP Socket Server (`tcp socket/`)
A simple TCP server implementation demonstrating basic socket programming concepts.

**Features:**
- Multi-port server support
- Basic client-server communication
- Server interconnectivity testing
- Simple hello-world protocol

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Installation

```bash
git clone <your-repository-url>
cd <repository-name>
```

## Usage Instructions

### P2P TCP Messaging System

**Starting the Server:**
```bash
cd "p2p tcp"
python servers.py
```
- Choose a port index from the displayed list (0-4)
- The server will automatically announce itself to other running servers

**Starting the Client:**
```bash
cd "p2p tcp"
python client.py
```
- Enter the server port you want to connect to
- Enter your username
- Start messaging by typing: `<recipient_username> <message>`

**Example:**
```
Enter server port: 5001
Enter your username: Alice
Bob Hello, how are you?
```

### RTT-Optimized Messaging

**Starting the Server:**
```bash
cd RTT
python serveurs.py
```
- Choose a port index from the displayed list
- Multiple servers can run simultaneously on different ports

**Starting the Client:**
```bash
cd RTT
python client.py
```
- Enter any server port to start
- Enter your username
- The client will automatically measure RTT to all servers and connect to the fastest one
- Start messaging: `<recipient_username> <message>`

**Example:**
```
Enter server port: 5001
Enter your username: Alice
Server 127.0.0.1:5001: RTT 0.000234 seconds
Server 127.0.0.1:5002: RTT 0.000156 seconds
Best server: 127.0.0.1:5002 with RTT 0.000156 seconds
Connected to best server on port 5002
```

### Basic TCP Socket Server

**Starting the Server:**
```bash
cd "tcp socket"
python serveurs.py
```
- Choose a port index from the displayed list
- The server will test connectivity to other servers automatically

**Testing the Server:**
You can test the server using telnet or a simple Python client:
```bash
telnet localhost 5001
```
Type `hello` and you should receive `world` as response.

## Protocol Details

### Message Format
The systems use a custom binary protocol with the following structure:
```
[1 byte: message_type][1 byte: message_subtype][2 bytes: message_length][2 bytes: reserved][variable: message_data]
```

### Message Types:
- `0`: Information request
- `1`: Server announcement/response
- `2`: User registration
- `3`: User message
- `4`: Echo request (RTT measurement)
- `5`: Disconnect notification

## Architecture

### P2P TCP System
```
Client A ──┐
           ├── Server 1 ──┬── Server 2 ──┬── Client C
Client B ──┘              └── Server 3 ──┘
```

### RTT System
```
Client ──> [RTT Test] ──> Server Selection ──> Optimal Server ──> Messaging
```

## Network Configuration

**Default Ports:** 5001, 5002, 5003, 5004, 5005

**Default Host:** 127.0.0.1 (localhost)

To modify these settings, edit the `ports` list in the respective server files.

## Features Comparison

| Feature | P2P TCP | RTT | Basic TCP |
|---------|---------|-----|-----------|
| Multi-server | ✅ | ✅ | ✅ |
| User messaging | ✅ | ✅ | ❌ |
| Server discovery | ✅ | ✅ | ✅ |
| RTT optimization | ❌ | ✅ | ❌ |
| Message forwarding | ✅ | ✅ | ❌ |
| Duplicate detection | ✅ | ✅ | ❌ |

## Troubleshooting

**Port already in use error:**
- Try a different port index
- Check if another instance is running: `lsof -i :5001`

**Connection refused:**
- Ensure the server is running before starting the client
- Check firewall settings
- Verify the correct port number

**Message not delivered:**
- Ensure the recipient username is correct
- Check if the recipient is connected to any server in the network
- Verify server connectivity

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve these network communication projects.

## License

This project is open source. 
