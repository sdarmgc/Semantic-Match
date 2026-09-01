# Semantic Match Backend API

A high-performance semantic similarity matching service that uses state-of-the-art sentence transformer models to find the most relevant matches between target phrases and a corpus of text.

## 🎯 Features

- **Semantic Similarity Matching**: Uses transformer-based models (LaBSE or MiniLM) to find semantically similar text matches
- **Multi-threaded Architecture**: Handles multiple client connections concurrently
- **TCP Socket Protocol**: Simple, reliable socket-based communication
- **Configurable Models**: Choose between LaBSE for multilingual support or MiniLM for lightweight performance
- **Batch Processing**: Processes multiple queries in a single request
- **Configurable Score Threshold**: Filter results by minimum similarity score

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd semantic-match
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Running the Server
```bash
python semantic_match/src/main.py
```

4. Custom configuration:
```bash
python semantic_match/src/main.py [HOST] [PORT] [MODEL_TYPE]
```
##### Parameters:
- HOST: Host address (default: '0.0.0.0')
- PORT: Port number (default: 9999)
- MODEL_TYPE: 'L' for LaBSE or 'M' for MiniLM (default: 'L')

##### Examples:
```bash
# Use LaBSE on localhost port 8080
python semantic_match/src/main.py 127.0.0.1 8080 L

# Use MiniLM on all interfaces port 9999
python semantic_match/src/main.py 0.0.0.0 9999 M
```

## 📡 API Protocol
#### Request Format
Send a JSON object via TCP socket with newline termination:
```bash
# json
{
  "targets": ["query text 1", "query text 2"],
  "corpus": ["candidate text 1", "candidate text 2", "..."],
  "score": 0.5
}
```
##### Fields:

- targets (required): Array of query strings to match
- corpus (required): Array of candidate strings to search against
- score (optional): Minimum similarity threshold (default: 0.0)

#### Response Format
```bash
# json
{
  "total_queries": 2,
  "results": [
    {
      "query_index": 0,
      "query": "original query text",
      "match_index": 1,
      "best_match": "best matching text from corpus",
      "similarity_score": 0.8521
    },
    {
      "query_index": 1,
      "query": "another query",
      "match_index": null,
      "best_match": null,
      "similarity_score": 0.0
    }
  ]
}
```

#### Error Response
```bash
# json
{
  "error": "Error message describing what went wrong"
}
```

#### Client Example (Python)
```bash
# python
import socket
import json

def send_query(host='127.0.0.1', port=9999):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    
    request = {
        "targets": ["artificial intelligence", "machine learning"],
        "corpus": ["AI technology", "data science", "deep learning"],
        "score": 0.3
    }
    
    client.send((json.dumps(request) + "\n").encode('utf-8'))
    
    response = client.recv(8192)
    return json.loads(response.decode('utf-8'))

if __name__ == "__main__":
    result = send_query()
    print(result)
```

#### Client Example (Laravel/PHP)
```bash
# php
<?php
$host = '127.0.0.1';
$port = 9999;

$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
socket_connect($socket, $host, $port);

$request = json_encode([
    'targets' => ['artificial intelligence', 'machine learning'],
    'corpus' => ['AI technology', 'data science', 'deep learning'],
    'score' => 0.3
]);

socket_write($socket, $request . "\n");
$response = socket_read($socket, 8192);
$result = json_decode($response, true);

socket_close($socket);
print_r($result);
?>
```

### 🧠 Model Options
Model&nbsp;&nbsp;&nbsp;&nbsp;Flag&nbsp;&nbsp;&nbsp;&nbsp;Size&nbsp;&nbsp;&nbsp;&nbsp;Best For
LaBSE&nbsp;&nbsp;&nbsp;&nbsp;L&nbsp;&nbsp;&nbsp;&nbsp;~1.2 GB&nbsp;&nbsp;&nbsp;&nbsp;Multilingual semantic search, cross-lingual matching
MiniLM&nbsp;&nbsp;&nbsp;&nbsp;M&nbsp;&nbsp;&nbsp;&nbsp;~120 MB&nbsp;&nbsp;&nbsp;&nbsp;Lightweight, faster inference for single language

### 📁 Project Structure
    semantic-match/
    ├── src/
    │   └── main.py          # Main server implementation
    ├── requirements.txt         # Python dependencies
    ├── README.md               # This file
    ├── LICENSE                 # License information
    └── .gitignore             # Git ignore rules


### 🙏 Acknowledgments
Sentence Transformers for the embedding models

LaBSE for multilingual embeddings

MiniLM for lightweight embeddings

###### This file is procdced by Deepseek. (chat.deepseek.com)
