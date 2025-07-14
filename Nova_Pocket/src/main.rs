use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce
};
use libp2p::{
    identity,
    swarm::{Swarm, SwarmEvent},
    Multiaddr, PeerId,
};
use std::error::Error;
use tokio::fs::File;
use tokio::io::AsyncReadExt;

// 1. Configurazione crittografia
const CHUNK_SIZE: usize = 1024 * 1024; // 1MB
type AesKey = [u8; 32]; // AES-256

// 2. Struttura per i chunk criptati
#[derive(Debug)]
struct EncryptedChunk {
    data: Vec<u8>,
    nonce: Vec<u8>,
}

// 3. Funzione per frammentare e criptare un file
async fn encrypt_file(path: &str, key: &AesKey) -> Result<Vec<EncryptedChunk>, Box<dyn Error>> {
    let mut file = File::open(path).await?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer).await?;

    let cipher = Aes256Gcm::new_from_slice(key)?;
    let chunks: Vec<_> = buffer.chunks(CHUNK_SIZE).collect();

    let mut encrypted_chunks = Vec::new();
    for (i, chunk) in chunks.iter().enumerate() {
        let nonce = Nonce::from_slice(&i.to_be_bytes()); // Nonce univoco per ogni chunk
        let encrypted_data = cipher.encrypt(&nonce, chunk.as_ref())?;
        
        encrypted_chunks.push(EncryptedChunk {
            data: encrypted_data,
            nonce: nonce.to_vec(),
        });
    }

    Ok(encrypted_chunks)
}

// 4. Configurazione rete P2P con libp2p
async fn setup_p2p_network() -> Result<(), Box<dyn Error>> {
    let local_key = identity::Keypair::generate_ed25519();
    let local_peer_id = PeerId::from(local_key.public());
    println!("Peer ID: {}", local_peer_id);

    let transport = libp2p::development_transport(local_key).await?;
    let mut swarm = Swarm::new(transport, MyBehaviour::default(), local_peer_id);

    // Ascolta su un indirizzo locale (es: /ip4/0.0.0.0/tcp/0)
    swarm.listen_on("/ip4/0.0.0.0/tcp/0".parse()?)?;

    // Esempio: connettiti a un altro peer (sostituisci con un indirizzo reale)
    if let Some(remote_peer) = std::env::args().nth(1) {
        let remote_addr: Multiaddr = remote_peer.parse()?;
        swarm.dial(remote_addr)?;
        println!("Connessione a: {}", remote_peer);
    }

    // Gestione eventi di rete
    loop {
        match swarm.select_next_some().await {
            SwarmEvent::NewListenAddr { address, .. } => {
                println!("In ascolto su: {}", address);
            }
            SwarmEvent::ConnectionEstablished { peer_id, .. } => {
                println!("Connesso a: {}", peer_id);
            }
            _ => {}
        }
    }
}

// 5. Comportamento del nodo P2P (semplificato)
#[derive(libp2p::NetworkBehaviour)]
struct MyBehaviour {
    floodsub: libp2p::floodsub::Floodsub,
}

impl Default for MyBehaviour {
    fn default() -> Self {
        Self {
            floodsub: libp2p::floodsub::Floodsub::new(PeerId::random()),
        }
    }
}

// 6. Funzione principale
#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Esempio: cripta un file
    let key: AesKey = [0u8; 32]; // Sostituisci con una chiave reale!
    let encrypted_chunks = encrypt_file("example.txt", &key).await?;
    println!("File criptato in {} chunk.", encrypted_chunks.len());

    // Avvia la rete P2P
    setup_p2p_network().await?;

    Ok(())
}

mod p2p;
mod storage;
mod ui;

use p2p::network::P2PNetwork;
use storage::encryption::{generate_key, encrypt_chunk};
use ui::cli::Cli;

#[tokio::main]
async fn main() {
    tokio::spawn(async {
    web::start_web_server().await;
    });

    println!("Server running at http://localhost:8080");
    let cli = Cli::parse();
    let key = generate_key();
    
    // Avvia la rete P2P
    let mut network = P2PNetwork::new().await;
    tokio::spawn(async move {
        network.start().await;
    });

    match cli.command {
        Command::Upload { path } => {
            let data = std::fs::read(&path).unwrap();
            let encrypted = encrypt_chunk(&data, &key).unwrap();
            println!("🔒 File criptato e pronto per l'upload!");
        },
        Command::Download { chunk_id } => {
            println!("Scarico chunk: {}", chunk_id);
        }
    }
}
