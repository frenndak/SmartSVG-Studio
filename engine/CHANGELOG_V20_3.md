# Historique V20.3

- Ajout d'un nœud autonome de diagnostic CUDA/VRAM, aucun modèle lancé.
- Ajout d'un nœud Line Art / Cricut protégé, héritant **sans modification** de V20.2.
- Ajout des politiques `protege`, `diagnostic`, `strict` et seuils libres configurables.
- Abstention explicite sans CUDA ou mémoire connue, seulement pour les appels IA internes.
- Masques `MASK` externes prioritaires même en mode strict, sans inférence supplémentaire.
- Mesures avant/après, chronomètre total, limites épistémiques détaillées et rapport JSON atomique.
- Garde-fous contre sondes CUDA absentes/partielles/incohérentes ; pas de réinitialisation des pics CUDA globaux.
- Six workflows nouveaux, anciens nœuds et workflows conservés.
- Tests adversariaux V20.3 et régression complète V20.2.
