from tools.js_bundler import JSBundler

bundler = JSBundler(
    entry_point="/storage/emulated/0/gitserver/om11/om11/static/js/app.js",
    output_path="om11/static/js/bundle.js",
    # validate_js=True,
    # log_level="DEBUG"  # DEBUG, INFO, WARNING, ERROR
)

if __name__ == "__main__":
    bundler.bundle()
