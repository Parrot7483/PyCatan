{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = [ pkgs.python310 
                          pkgs.python310Packages.pytest
                          pkgs.bash 
                          pkgs.tree
                        ];

    shellHook = ''
      alias tree='tree -I "__pycache__"'
    '';
}
