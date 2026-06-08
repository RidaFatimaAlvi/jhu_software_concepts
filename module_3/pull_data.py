import subprocess

print("Starting Pull Data process...")

subprocess.run(["python", "scrape.py"])
subprocess.run(["python", "load_data.py"])

print("Pull Data process finished.")