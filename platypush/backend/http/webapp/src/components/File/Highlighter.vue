<script>
const languageMappers = {
  actionscript: {
    extensions: ['.as'],
    types: ['text/x-actionscript'],
  },
  ada: {
    extensions: ['.ada', '.adb', '.ads'],
    types: ['text/x-ada'],
  },
  apache: {
    extensions: ['.htaccess', '.htpasswd'],
    types: ['text/x-apache'],
  },
  arduino: {
    extensions: ['.ino'],
    types: ['text/x-arduino'],
  },
  autoit: {
    extensions: ['.au3'],
    types: ['text/x-autoit'],
  },
  awk: {
    extensions: ['.awk'],
    types: ['text/x-awk'],
  },
  bash: {
    extensions: ['.sh', '.bash'],
    types: ['text/x-sh'],
  },
  basic: {
    extensions: ['.bas', '.basic'],
    types: ['text/x-basic'],
  },
  bnf: {
    extensions: ['.bnf'],
    types: ['text/x-bnf'],
  },
  c: {
    extensions: ['.c', '.h'],
    types: ['text/x-c'],
  },
  clojure: {
    extensions: ['.clj', '.cljc', '.cljx', '.cljs', '.edn'],
    types: ['text/x-clojure'],
  },
  cmake: {
    extensions: ['.cmake', '.cmake.in'],
    types: ['text/x-cmake'],
  },
  coffeescript: {
    extensions: ['.coffee'],
    types: ['text/x-coffeescript'],
  },
  cpp: {
    extensions: ['.cpp', '.cc', '.cxx', '.c++', '.h', '.hh', '.hpp', '.hxx', '.h++'],
    types: ['text/x-c++src'],
  },
  crystal: {
    extensions: ['.cr'],
    types: ['text/x-crystal'],
  },
  css: {
    extensions: ['.css'],
    types: ['text/css'],
  },
  d: {
    extensions: ['.d'],
    types: ['text/x-d'],
  },
  dart: {
    extensions: ['.dart'],
    types: ['text/x-dart'],
  },
  delphi: {
    extensions: ['.pas', '.dpr', '.dfm', '.dpk', '.dproj'],
    types: ['text/x-pascal'],
  },
  diff: {
    extensions: ['.diff', '.patch'],
    types: ['text/x-diff'],
  },
  dns: {
    extensions: ['.zone', '.arpa'],
    types: ['text/x-dns'],
  },
  dockerfile: {
    extensions: ['Dockerfile'],
    types: ['text/x-dockerfile'],
  },
  dos: {
    extensions: ['.bat', '.cmd'],
    types: ['text/x-dos'],
  },
  dsconfig: {
    extensions: ['.dsconfig'],
    types: ['text/x-dsconfig'],
  },
  dts: {
    extensions: ['.dts', '.dtsi'],
    types: ['text/x-dts'],
  },
  dust: {
    extensions: ['.dust'],
    types: ['text/x-dust'],
  },
  ebnf: {
    extensions: ['.ebnf'],
    types: ['text/x-ebnf'],
  },
  elixir: {
    extensions: ['.ex', '.exs'],
    types: ['text/x-elixir'],
  },
  elm: {
    extensions: ['.elm'],
    types: ['text/x-elm'],
  },
  erlang: {
    extensions: ['.erl'],
    types: ['text/x-erlang'],
  },
  excel: {
    extensions: ['.xls', '.xlsx'],
    types: ['text/x-excel'],
  },
  fortran: {
    extensions: ['.f', '.f77', '.f90', '.f95'],
    types: ['text/x-fortran'],
  },
  fsharp: {
    extensions: ['.fs', '.fsi', '.fsx', '.fsscript'],
    types: ['text/x-fsharp'],
  },
  gherkin: {
    extensions: ['.feature'],
    types: ['text/x-feature'],
  },
  go: {
    extensions: ['.go'],
    types: ['text/x-go'],
  },
  gradle: {
    extensions: ['.gradle'],
    types: ['text/x-gradle'],
  },
  graphql: {
    extensions: ['.graphql'],
    types: ['text/x-graphql'],
  },
  groovy: {
    extensions: ['.groovy', '.gradle'],
    types: ['text/x-groovy'],
  },
  handlebars: {
    extensions: ['.hbs', '.handlebars'],
    types: ['text/x-handlebars-template'],
  },
  haskell: {
    extensions: ['.hs', '.lhs'],
    types: ['text/x-haskell'],
  },
  http: {
    extensions: ['.http'],
    types: ['message/http'],
  },
  ini: {
    extensions: ['.ini', '.toml'],
    types: ['text/x-ini'],
  },
  java: {
    extensions: ['.java'],
    types: ['text/x-java'],
  },
  html: {
    extensions: ['.html', '.htm'],
    types: ['text/html'],
  },
  javascript: {
    extensions: ['.js', '.mjs'],
    types: ['application/javascript'],
  },
  json: {
    extensions: ['.json'],
    types: ['application/json'],
  },
  julia: {
    extensions: ['.jl'],
    types: ['text/x-julia'],
  },
  kotlin: {
    extensions: ['.kt', '.kts'],
    types: ['text/x-kotlin'],
  },
  latex: {
    extensions: ['.tex'],
    types: ['text/x-latex'],
  },
  less: {
    extensions: ['.less'],
    types: ['text/x-less'],
  },
  lisp: {
    extensions: ['.lisp', '.lsp'],
    types: ['text/x-lisp'],
  },
  llvm: {
    extensions: ['.ll'],
    types: ['text/x-llvm'],
  },
  lua: {
    extensions: ['.lua'],
    types: ['text/x-lua'],
  },
  makefile: {
    extensions: ['Makefile'],
    types: ['text/x-makefile'],
  },
  markdown: {
    extensions: ['.md', '.markdown'],
    types: ['text/markdown'],
  },
  mathematica: {
    extensions: ['.m'],
    types: ['text/x-mathematica'],
  },
  matlab: {
    extensions: ['.m'],
    types: ['text/x-matlab'],
  },
  nginx: {
    extensions: ['.nginx', 'nginx.conf'],
    contains: ['/sites-available/', '/sites-enabled/'],
    types: ['text/x-nginx-conf'],
  },
  nim: {
    extensions: ['.nim', '.nimble'],
    types: ['text/x-nim'],
  },
  nix: {
    extensions: ['.nix'],
    types: ['text/x-nix'],
  },
  objectivec: {
    extensions: ['.m'],
    types: ['text/x-objectivec'],
  },
  ocaml: {
    extensions: ['.ml', '.mli'],
    types: ['text/x-ocaml'],
  },
  perl: {
    extensions: ['.pl', '.pm'],
    types: ['text/x-perl'],
  },
  pgsql: {
    extensions: ['.pgsql'],
    types: ['text/x-pgsql'],
  },
  php: {
    extensions: ['.php'],
    types: ['text/x-php'],
  },
  plaintext: {
    extensions: ['.txt']
  },
  powershell: {
    extensions: ['.ps1', '.psm1', '.psd1'],
    types: ['text/x-powershell'],
  },
  prolog: {
    extensions: ['.pro', '.prolog'],
    types: ['text/x-prolog'],
  },
  protobuf: {
    extensions: ['.proto'],
    types: ['text/x-protobuf'],
  },
  puppet: {
    extensions: ['.pp'],
    types: ['text/x-puppet'],
  },
  python: {
    extensions: ['.py'],
    types: ['text/x-python'],
  },
  r: {
    extensions: ['.r'],
    types: ['text/x-r'],
  },
  ruby: {
    extensions: ['.rb'],
    types: ['text/x-ruby'],
  },
  rust: {
    extensions: ['.rs'],
    types: ['text/x-rust'],
  },
  scala: {
    extensions: ['.scala'],
    types: ['text/x-scala'],
  },
  scheme: {
    extensions: ['.scm', '.ss'],
    types: ['text/x-scheme'],
  },
  scss: {
    extensions: ['.scss'],
    types: ['text/x-scss'],
  },
  smalltalk: {
    extensions: ['.st'],
    types: ['text/x-stsrc'],
  },
  sql: {
    extensions: ['.sql'],
    types: ['text/x-sql'],
  },
  swift: {
    extensions: ['.swift'],
    types: ['text/x-swift'],
  },
  tcl: {
    extensions: ['.tcl'],
    types: ['text/x-tcl'],
  },
  typescript: {
    extensions: ['.ts'],
    types: ['application/typescript'],
  },
  vbnet: {
    extensions: ['.vb'],
    types: ['text/x-vb'],
  },
  vbscript: {
    extensions: ['.vbs'],
    types: ['text/vbscript'],
  },
  vhdl: {
    extensions: ['.vhd', '.vhdl'],
    types: ['text/x-vhdl'],
  },
  vim: {
    extensions: ['.vim', '.vimrc'],
    types: ['text/x-vim'],
  },
  wasm: {
    extensions: ['.wasm'],
    types: ['application/wasm'],
  },
  x86asm: {
    extensions: ['.asm', '.s'],
    types: ['text/x-asm'],
  },
  xml: {
    extensions: ['.xml'],
    types: ['application/xml'],
  },
  yaml: {
    extensions: ['.yaml', '.yml'],
    types: ['text/x-yaml'],
  },
}

export default {
  methods: {
    getLanguageType(file) {
      for (const [language, mapper] of Object.entries(languageMappers)) {
        const matchingExtensions = mapper.extensions?.filter((ext) => file.path.toLowerCase().endsWith(ext))
        if (matchingExtensions?.length) {
          return language
        }

        const matchingContains = mapper.contains?.filter((contains) => file.path.toLowerCase().includes(contains))
        if (matchingContains?.length) {
          return language
        }

        const matchingTypes = mapper.types?.filter((type) => file.type === type)
        if (matchingTypes?.length) {
          return language
        }
      }

      return 'plaintext'
    },
  },
}
</script>
