
from app.models.databases.repository import Repository


class TestCaseData(Repository):
	
	def __init__(self, supabase_client):
		self.db = supabase_client
