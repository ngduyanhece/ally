from supabase.client import Client, ClientOptions, create_client

SUPABASE_URL = 'https://vduyhyzdrhvvgqyovyhl.supabase.co'
SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZkdXloeXpkcmh2dmdxeW92eWhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDE4NDQ2NjQsImV4cCI6MjAxNzQyMDY2NH0.upozyYacb36cM17FZqNakkQF2NxQHKFaVimADaE2wmY'

def get_foodally_client() -> Client:
	# TODO we should include the supabase_url and supabase_service_key in the brain setting
	supabase_client: Client = create_client(
		SUPABASE_URL, 
		SUPABASE_SERVICE_KEY,
		options=ClientOptions(
			auto_refresh_token=True,
			persist_session=True,
		)
	)
	return supabase_client