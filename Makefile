dev:
	py -m nuitka --enable-plugin=tk-inter --standalone --include-data-files=src/config.json=config.json src/main.py
prod:
	py -m nuitka --onefile-no-compression --company-name="XLuma" --product-name="Avatar Preset Manager" --file-version=1.0 --product-version=1.0 --enable-plugin=tk-inter --onefile-tempdir-spec="{CACHE_DIR}/AvatarPresetManager/{VERSION}" --standalone --onefile --include-onefile-external-data=src/config.json src/main.py