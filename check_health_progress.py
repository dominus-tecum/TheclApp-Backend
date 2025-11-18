import os

def check_health_progress_modules():
    health_progress_path = "app/health_progress"
    
    if not os.path.exists(health_progress_path):
        print(f"❌ Directory {health_progress_path} does not exist!")
        return
    
    print("🔍 Health Progress Modules Found:")
    for item in os.listdir(health_progress_path):
        item_path = os.path.join(health_progress_path, item)
        if os.path.isdir(item_path):
            # Check if it has routers.py
            routers_file = os.path.join(item_path, "routers.py")
            if os.path.exists(routers_file):
                print(f"✅ {item}: has routers.py")
            else:
                print(f"❌ {item}: missing routers.py")

if __name__ == "__main__":
    check_health_progress_modules()