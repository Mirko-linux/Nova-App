use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce
};
use std::io;

pub const CHUNK_SIZE: usize = 1024 * 1024; // 1MB

/// Genera una chiave AES-256 sicura
pub fn generate_key() -> [u8; 32] {
    let mut key = [0u8; 32];
    OsRng.fill_bytes(&mut key);
    key
}

/// Cripta un chunk di dati
pub fn encrypt_chunk(data: &[u8], key: &[u8; 32]) -> Result<Vec<u8>, aes_gcm::Error> {
    let cipher = Aes256Gcm::new_from_slice(key)?;
    let nonce = Nonce::from_slice(&[0u8; 12]); // Sostituire con nonce univoco
    cipher.encrypt(nonce, data)
}
