1. backend on PORT 8000 
2. Sync service on PORT 8001

3. User uploads an image. 

python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn \
  --age 35 \
  --gender M \
  --notes "Security guard"


4. Embeddings are generated and stored on psql

5. sync api fetches new embeddings


6. python main.py --mode live --method retinaface --recognize --similarity-threshold 0.6 


