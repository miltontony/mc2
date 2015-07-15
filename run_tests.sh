rm -rf project/.test_* && py.test -s --ds=test_settings --verbose --cov ./unicoremc unicoremc "$@"
