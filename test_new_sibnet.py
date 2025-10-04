#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append("linkfinderbot/src/bot/utils")

def test_new_sibnet():
    """Test de la nouvelle fonction Sibnet"""
    
    from sibnet_simple import sibnet_internal_search, get_sibnet_share_link
    
    query = "ONE PIECE episode 1089"
    
    print("🧪 TEST SIBNET AMÉLIORÉ")
    print("=" * 50)
    print(f"Query: {query}")
    print()
    
    # Test 1: fonction interne
    print("📍 Test 1: sibnet_internal_search")
    result1 = sibnet_internal_search(query)
    print(f"Résultat: {result1}")
    print()
    
    # Test 2: fonction complète
    print("📍 Test 2: get_sibnet_share_link")
    result2 = get_sibnet_share_link(query)
    print(f"Résultat: {result2}")
    print()
    
    # Test avec d'autres queries
    queries_test = [
        "ONE PIECE 1089",
        "One Piece episode 1006",
        "anime One Piece"
    ]
    
    print("📍 Tests additionnels:")
    for q in queries_test:
        print(f"  Query: {q}")
        result = get_sibnet_share_link(q)
        print(f"  Résultat: {result}")
        print()
    
    print("✅ Tests terminés")

if __name__ == "__main__":
    test_new_sibnet()