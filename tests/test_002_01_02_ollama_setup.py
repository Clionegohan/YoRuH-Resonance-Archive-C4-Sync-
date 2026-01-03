"""
Test for Subtask 002-01-02: Ollama環境構築とモデル準備

このテストはAcceptance Criteriaから導出されています。
"""
import pytest
from src.utils.ollama_client import OllamaClient


def test_ollama_connection():
    """AC: http://localhost:11434でOllamaに接続できること"""
    client = OllamaClient()
    assert client.is_available()


def test_ollama_models_list():
    """AC: Ollamaに接続できる場合、利用可能なモデルリストを取得すること"""
    client = OllamaClient()
    models = client.list_models()
    assert models is not None
    assert len(models) > 0


def test_llama31_model_exists():
    """AC: llama3.1:8bモデルがダウンロードされていること"""
    client = OllamaClient()
    models = client.list_models()
    model_names = [m["name"] for m in models]
    assert "llama3.1:8b" in model_names


def test_mxbai_model_exists():
    """AC: mxbai-embed-largeモデルがダウンロードされていること"""
    client = OllamaClient()
    models = client.list_models()
    model_names = [m["name"] for m in models]
    assert "mxbai-embed-large:latest" in model_names


def test_llama31_generation():
    """AC: テスト用テキストをllama3.1に送信した場合、応答を受け取ること"""
    client = OllamaClient()
    response = client.generate(
        model="llama3.1:8b",
        prompt="こんにちは"
    )
    assert response is not None
    assert len(response) > 0


def test_mxbai_embedding():
    """AC: テスト用テキストをmxbai-embed-largeで埋め込みした場合、1024次元のベクトルを受け取ること"""
    client = OllamaClient()
    vector = client.embed(
        model="mxbai-embed-large",
        text="テストテキスト"
    )
    assert vector is not None
    assert len(vector) == 1024
