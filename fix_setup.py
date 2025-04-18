import os
import json
import re
import sys

def main():
    print("\n=== TELEGRAM BOT SETUP FIXER ===\n")
    print("This script will help fix common issues with your bot setup.")
    
    # 1. Check config.py
    print("\n[1] Checking config.py...")
    if not os.path.exists("config.py"):
        print("❌ ERROR: config.py not found!")
        return
        
    # Read config.py
    with open("config.py", "r") as f:
        config_content = f.read()
        
    # Extract channel IDs
    storage_match = re.search(r'STORAGE_CHANNEL\s*=\s*([0-9-]+)', config_content)
    if not storage_match:
        print("❌ ERROR: Could not find STORAGE_CHANNEL in config.py")
        return
        
    storage_channel = storage_match.group(1)
    print(f"Current storage channel ID: {storage_channel}")
    
    # 2. Check admin_config.json
    print("\n[2] Checking admin_config.json...")
    admin_config_path = "config/admin_config.json"
    if not os.path.exists(admin_config_path):
        print(f"❌ ERROR: {admin_config_path} not found!")
        return
        
    try:
        with open(admin_config_path, "r") as f:
            admin_config = json.load(f)
            
        admin_storage = admin_config.get("storage_channel")
        print(f"Current admin config storage channel: {admin_storage}")
        
        # Check if values match
        if str(admin_storage) != storage_channel:
            print("⚠️ WARNING: Channel IDs don't match between config.py and admin_config.json!")
            
            # Ask which one to use
            print("\nWhich channel ID should be used?")
            print(f"1. From config.py: {storage_channel}")
            print(f"2. From admin_config.json: {admin_storage}")
            
            choice = input("Enter 1 or 2 (or press Enter to keep both): ")
            
            if choice == "1":
                # Update admin_config.json
                admin_config["storage_channel"] = int(storage_channel)
                with open(admin_config_path, "w") as f:
                    json.dump(admin_config, f, indent=4)
                print(f"✅ Updated admin_config.json to use channel ID: {storage_channel}")
                
            elif choice == "2":
                # Update config.py
                new_config = re.sub(
                    r'STORAGE_CHANNEL\s*=\s*[0-9-]+',
                    f'STORAGE_CHANNEL = {admin_storage}',
                    config_content
                )
                
                # Also update POST_CHANNEL and DUMP_CHANNEL
                new_config = re.sub(
                    r'POST_CHANNEL\s*=\s*[0-9-]+',
                    f'POST_CHANNEL = {admin_storage}',
                    new_config
                )
                
                new_config = re.sub(
                    r'DUMP_CHANNEL\s*=\s*[0-9-]+',
                    f'DUMP_CHANNEL = {admin_storage}',
                    new_config
                )
                
                with open("config.py", "w") as f:
                    f.write(new_config)
                
                print(f"✅ Updated config.py to use channel ID: {admin_storage}")
        else:
            print("✅ Channel IDs match between config files")
            
    except Exception as e:
        print(f"❌ ERROR reading admin_config.json: {str(e)}")
        return
    
    # 3. Fix channel ID format
    print("\n[3] Checking channel ID format...")
    
    # Get current channel ID (from config.py or admin_config.json)
    current_id = storage_channel
    if choice == "2":
        current_id = str(admin_storage)
        
    # Check if format is correct
    if not current_id.startswith("-100"):
        print("⚠️ WARNING: Channel ID doesn't start with -100, which is the usual format")
        
        # Suggest fixes
        suggestions = []
        
        # Try to convert to proper format
        if current_id.startswith("-1001"):
            suggestions.append(current_id.replace("-1001", "-100"))
        elif not current_id.startswith("-"):
            suggestions.append(f"-100{current_id}")
        else:
            # Just strip the minus and add -100
            suggestions.append(f"-100{current_id.lstrip('-')}")
            
        # Also add variation with -1001
        suggestions.append(f"-1001{current_id.lstrip('-')}")
        
        print("\nSuggested formats to try:")
        for i, suggestion in enumerate(suggestions):
            print(f"{i+1}. {suggestion}")
            
        print("\nTo try these formats:")
        print("1. Edit config.py manually or use /setchannel in your bot")
        print("2. Make sure your bot is an admin in the channel with 'Post Messages' permission")
        print("3. Restart your bot to apply changes")
        
    else:
        print("✅ Channel ID format looks correct")
    
    # 4. Instructions for verifying permissions
    print("\n[4] Instructions to verify bot permissions:")
    print("1. Make sure your bot is a member of the channel")
    print("2. Go to channel settings > Administrators")
    print("3. Find your bot or add it as an administrator")
    print("4. Enable these permissions:")
    print("   - Post Messages (essential)")
    print("   - Edit Messages")
    print("   - Delete Messages")
    print("5. Save changes and restart your bot")
    
    print("\n=== SETUP CHECK COMPLETED ===")
    print("\nIf you're still having issues:")
    print("1. Use the /setchannel command in your bot to update the channel")
    print("2. The improved channel handling code should now be more flexible with different ID formats")
    print("3. Make sure your channel exists and the bot has proper admin rights")

if __name__ == "__main__":
    main() 