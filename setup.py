from setuptools import setup, find_packages

setup(
	name="lilbinboy",
	version="0.1.0",  # Update as needed
	description="Lil' Bin Boy will do it!",
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
	author="Michael Jordan",
	author_email="michael@glowingpixel.com",
	url="https://github.com/mjiggidy/lilbinboy",  # Replace with your repository URL
	packages=find_packages(include=["lilbinboy", "lilbinboy.*"]),
	install_requires=[
		"avbutils @ git+https://github.com/mjiggidy/avbutils.git#egg=avbutils",
		"timecode @ git+https://github.com/mjiggidy/timecode.git#egg=timecode",
		"pyavb",
		"PySide6"
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",  # Update if using a different license
		"Operating System :: OS Independent",
	],
	python_requires=">=3.7",
	include_package_data=True,
	entry_points={
		"console_scripts": [
			"lilbinboy=lilbinboy.__main__:main",  # Updated to use __main__.py as the entry point
		],
	},
)