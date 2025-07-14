use libp2p::{
    kad::{Kademlia, Record},
    swarm::{Swarm, SwarmEvent},
    Multiaddr, PeerId,
};

pub struct P2PNetwork {
    pub swarm: Swarm<MyBehaviour>,
}

impl P2PNetwork {
    pub async fn new() -> Self {
        let local_key = libp2p::identity::Keypair::generate_ed25519();
        let local_peer_id = PeerId::from(local_key.public());
        
        let transport = libp2p::development_transport(local_key).await.unwrap();
        let behaviour = MyBehaviour::default();
        
        P2PNetwork {
            swarm: Swarm::new(transport, behaviour, local_peer_id),
        }
    }

    pub async fn start(&mut self) {
        self.swarm.listen_on("/ip4/0.0.0.0/tcp/0".parse().unwrap()).unwrap();
        
        loop {
            match self.swarm.select_next_some().await {
                SwarmEvent::NewListenAddr { address, .. } => {
                    println!("📡 In ascolto su: {}", address);
                },
                _ => {}
            }
        }
    }
}
