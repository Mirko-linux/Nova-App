use std::collections::HashMap;

pub struct ChunkManager {
    pub local_chunks: HashMap<String, Vec<u8>>, // ChunkID -> Dati criptati
}

impl ChunkManager {
    pub fn new() -> Self {
        ChunkManager {
            local_chunks: HashMap::new(),
        }
    }

    pub fn add_chunk(&mut self, chunk_id: String, data: Vec<u8>) {
        self.local_chunks.insert(chunk_id, data);
    }
}
