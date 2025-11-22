from werkzeug.security import check_password_hash

hash_val = 'scrypt:32768:8:1$iXhic7CwyrUMot9J$1b45e822d68a92b69355f950685dc64a32969d7327dbb92739efb9c8592c4ce'
password = 'password123'

print(f"Match: {check_password_hash(hash_val, password)}")


