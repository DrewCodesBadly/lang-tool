pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'langtool'
gnome = import('gnome')

gnome.compile_resources('langtool',
  'langtool.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'langtool.in',
  output: 'langtool',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

langtool_sources = [
  '__init__.py',
  'main.py',
  'config.py',
  'archive_view.py',
  'languages_view.py',
  'notes_view.py',
  'ollama_thread.py',
  'pages.py',
  'resources_view.py',
  'writing_view.py',
]

install_data(langtool_sources, install_dir: moduledir)
