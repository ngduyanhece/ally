from fastapi.middleware.cors import CORSMiddleware

# origins = [
# 	"http://localhost",
# 	"http://localhost:3000",
# 	"http://localhost:3001",
# 	"http://52.74.55.75:3000",
# 	"https://52.74.55.75:3000"
# 	"*",
# ]


def add_cors_middleware(app):
  	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)
