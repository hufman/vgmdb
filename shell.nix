{ pkgs ? import <nixpkgs> {} }:

(pkgs.buildFHSEnv {
  name = "vgmdbapi";
  targetPkgs = pkgs: (with pkgs; [
    (python311.withPackages( p: [ p.cython ]))
    virtualenv
    libxml2
    libxslt
  ]);
}).env
