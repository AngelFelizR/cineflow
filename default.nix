let
  pkgs = import (fetchTarball "https://github.com/rstats-on-nix/nixpkgs/archive/2025-12-02.tar.gz") {};

  pyconf = builtins.attrValues {
    inherit (pkgs.python313Packages)
      pip
      ipykernel
      flask
      flask-login
      flask-bcrypt
      sqlalchemy
      pymssql
      pandas
      openpyxl
      reportlab
      xhtml2pdf;
  };

  system_packages = builtins.attrValues {
    inherit (pkgs)
      glibcLocales
      nix
      python313
      freetds;
  };

  shell = pkgs.mkShell {
    LOCALE_ARCHIVE = if pkgs.system == "x86_64-linux" then "${pkgs.glibcLocales}/lib/locale/locale-archive" else "";
    LANG = "en_US.UTF-8";
    LC_ALL = "en_US.UTF-8";
    LC_TIME = "en_US.UTF-8";
    LC_MONETARY = "en_US.UTF-8";
    LC_PAPER = "en_US.UTF-8";
    LC_MEASUREMENT = "en_US.UTF-8";
    buildInputs = [ pyconf system_packages ];
  };
in
  {
    inherit pkgs shell;
  }
