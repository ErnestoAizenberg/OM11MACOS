# args_parser.py
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Flask app with Redis support.")
    parser.add_argument("--server_address", type=str, help="URL server running in")
    parser.add_argument("--secret_key", type=str, help="Secret key for Flask app")
    parser.add_argument("--redis_host", type=str, help="Redis server host")
    parser.add_argument("--redis_port", type=int, help="Redis server port")
    parser.add_argument("--redis_db", type=int, help="Redis database number")
    return parser.parse_args()
