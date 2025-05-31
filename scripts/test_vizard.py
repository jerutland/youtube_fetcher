from opus_automation.vizard_client import submit_video

yt_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with real link
result = submit_video(yt_link)

print("✅ Clip submitted:")
print(result)
