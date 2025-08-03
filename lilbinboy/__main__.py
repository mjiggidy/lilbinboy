"""Main entrypoint as module"""

if __name__ == "__main__":
	import multiprocessing
	from . import main
	
	multiprocessing.freeze_support()
	main()