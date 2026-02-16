PROJECT=ggszk-lab
REGION=asia-northeast1
SERVICE=lda-demo
URL=https://$(SERVICE)-655957689949.$(REGION).run.app

deploy:
	gcloud run deploy $(SERVICE) \
	  --source . \
	  --region $(REGION) \
	  --platform managed \
	  --allow-unauthenticated \
	  --memory 2Gi \
	  --timeout 120 \
	  --project $(PROJECT)

logs:
	gcloud run services logs read $(SERVICE) \
	  --region $(REGION) \
	  --project $(PROJECT) \
	  --limit 50

open:
	open $(URL)

dev:
	.venv/bin/python app.py
