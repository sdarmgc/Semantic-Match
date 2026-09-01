import socket
import json
import sys
import threading
from sentence_transformers import SentenceTransformer, util

def handle_client(client_socket, addr, MODEL):
    """Worker function to process individual client requests in a dedicated thread."""
    try:
        data = b""
        # Robust streaming loop: continuously read packets until the newline delimiter is verified
        while True:
            chunk = client_socket.recv(8192) # Increased buffer size for larger data text arrays
            if not chunk:
                break
            data += chunk
            if b"\n" in chunk: # Safe verification check per network packet arrival
                break

        if not data:
            return

        try:
            payload = json.loads(data.decode('utf-8'))
            # print(f"[{payload}]", flush=True)
            targets = payload.get("targets", [])
            corpus = payload.get("corpus", [])
            score = payload.get("score", 0.0)

            if not targets or not corpus:
                raise ValueError("Both 'targets' and 'corpus' arrays must contain values.")

            print(f"[{addr[0]}] Processing extraction matrix match...", flush=True)
            
            # Run embeddings matching in memory using global MODEL reference
            corpus_embeddings = MODEL.encode(corpus, convert_to_tensor=True)
            query_embeddings = MODEL.encode(targets, convert_to_tensor=True)
            similarity_matrix = util.cos_sim(query_embeddings, corpus_embeddings)

            results_list = []
            for idx, query in enumerate(targets):
                # Ensure the index stays within the row bounds of the similarity matrix
                if idx >= similarity_matrix.shape[0]:
                    break
                query_scores = similarity_matrix[idx]
                best_match_idx = query_scores.argmax().item()
                best_score = query_scores[best_match_idx].item()
                
                # Double-check that PyTorch's column lookup index exists in your corpus array
                if best_match_idx < len(corpus) and best_score >= score:
                    best_sentence = corpus[best_match_idx]
                    final_score = round(best_score, 4)
                else:
                    best_sentence = None
                    final_score = 0.0

                results_list.append({
                    "query_index": idx,
                    "query": query,
                    "match_index": best_match_idx if best_sentence else None,
                    "best_match": best_sentence,
                    "similarity_score": final_score
                })

            response_data = {"total_queries": len(targets), "results": results_list}
            
        except Exception as e:
            response_data = {"error": str(e)}
            
        # Transmit the computed results block back to the Laravel socket connection pool
        response_bytes = (json.dumps(response_data) + "\n").encode('utf-8')
        client_socket.sendall(response_bytes)
        # print(f"[{response_bytes}]", flush=True)

    except Exception as e:
        print(f"Error handling client connection socket: {str(e)}", file=sys.stderr, flush=True)
    finally:
        client_socket.close()
        print(f"[{addr[0]}] Request completed and socket connection released.", flush=True)

def main():
    args = sys.argv[1:]
    HOST = args[0] if len(args) > 0 else '0.0.0.0'
    PORT = int(args[1]) if len(args) > 1 else 9999
    modelType = args[2] if len(args) > 2 else 'L' # 'L' for LaBSE, 'M' for MiniLM

    # Load the model once globally at the system level on script startup
    try:
        if modelType == 'L':
            print("Loading LaBSE model into system RAM...", flush=True)
            MODEL = SentenceTransformer("sentence-transformers/LaBSE")
        else:
            print("Loading paraphrase-multilingual-MiniLM model into memory...", flush=True)
            MODEL = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        print("Model successfully loaded and warmed up.", flush=True)
    except Exception as e:
        print(f"CRITICAL: Failed to load model. Error: {str(e)}", file=sys.stderr, flush=True)
        sys.exit(1)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(50) # Expanded queue depth to safely hold traffic peaks
    
    print(f"Listening for TCP socket streams on {HOST}:{PORT}...", flush=True)

    while True:
        try:
            client_socket, addr = server.accept()
            # Hand off the connection to a background thread instantly to avoid blocking other users
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, MODEL))
            client_thread.daemon = True # Allows fast process termination when shutting down service
            client_thread.start()
        except KeyboardInterrupt:
            print("\nShutting down TCP server daemon safely.", flush=True)
            break
        except Exception as e:
            print(f"Server loop error encountered: {str(e)}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
