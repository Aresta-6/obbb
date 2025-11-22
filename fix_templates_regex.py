import os
import re

# Mapping of old endpoint names to new blueprint endpoints
endpoint_map = {
    'index': 'main.index',
    'books': 'main.books',
    'book_details': 'main.book_details',
    
    'login': 'auth.login',
    'register': 'auth.register',
    'logout': 'auth.logout',
    
    'profile': 'user.profile',
    'my_borrows': 'user.my_borrows',
    'my_reservations': 'user.my_reservations',
    'cancel_reservation': 'user.cancel_reservation',
    'return_book': 'user.return_book',
    'borrow': 'user.borrow',
    'reserve_book': 'user.reserve_book',
    'notifications': 'user.notifications',
    
    'admin_dashboard': 'admin.dashboard',
    'admin_manage_books': 'admin.manage_books',
    'admin_manage_copies': 'admin.manage_copies',
    'admin_add_copy': 'admin.add_copy',
    'admin_delete_copy': 'admin.delete_copy',
    'admin_edit_book': 'admin.edit_book',
    'admin_delete_book': 'admin.delete_book',
    'admin_add_book': 'admin.add_book',
    'admin_reservations': 'admin.reservations',
    'admin_cancel_reservation': 'admin.cancel_reservation',
    'admin_fulfill_reservation': 'admin.fulfill_reservation',
    'admin_remind_user': 'admin.remind_user',
    'admin_manage_returns': 'admin.manage_returns',
    'admin_force_return': 'admin.force_return',
}

def replace_endpoints(match):
    endpoint = match.group(1)
    if endpoint in endpoint_map:
        return f"url_for('{endpoint_map[endpoint]}'"
    return match.group(0)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to match url_for('endpoint' or url_for("endpoint"
    # We match the opening part of url_for call up to the closing quote of the endpoint
    # Pattern: url_for\s*\(\s*['"]([^'"]+)['"]
    pattern = re.compile(r"url_for\s*\(\s*['\"]([^'\"]+)['\"]")
    
    new_content = pattern.sub(replace_endpoints, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            process_file(os.path.join(root, file))


