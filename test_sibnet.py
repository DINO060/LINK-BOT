import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'linkfinderbot', 'src', 'bot', 'utils'))

from sibnet_simple import get_sibnet_share_link

# Test de la recherche Sibnet
query = "ONE PIECE episode 1089"
print(f"Test recherche: {query}")
result = get_sibnet_share_link(query)
print(f"Résultat: {result}")