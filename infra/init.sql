-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create memory table for storing conversation logs
CREATE TABLE IF NOT EXISTS memory_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_query TEXT NOT NULL,
    response TEXT NOT NULL,
    intent VARCHAR(100),
    meta JSONB DEFAULT '{}',
    embedding VECTOR(1024)
);

-- Create RAG chunks table
CREATE TABLE IF NOT EXISTS kb_chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    source VARCHAR(500),
    chunk_index INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_memory_logs_timestamp ON memory_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_memory_logs_intent ON memory_logs(intent);
CREATE INDEX IF NOT EXISTS idx_kb_chunks_source ON kb_chunks(source);
CREATE INDEX IF NOT EXISTS idx_memory_logs_embedding ON memory_logs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_kb_chunks_embedding ON kb_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);