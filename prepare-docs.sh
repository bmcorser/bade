#! /bin/bash

zip_name="docs-$(git rev-parse HEAD | cut -c 1-7).zip"
pushd docs
make html
pushd build/html
zip -r $zip_name .
popd
popd
mv docs/build/html/$zip_name ./
