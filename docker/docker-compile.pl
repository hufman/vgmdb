#!/usr/bin/env perl
# Modified from http://3ofcoins.net/2013/09/22/flat-docker-images/
 
use feature 'switch';
use strict;
use warnings;
 
use Data::Dumper;
use File::Basename;
use File::Copy;
use File::Path qw/make_path/;
use File::Temp qw/tempdir/;
use Getopt::Long;
 
use JSON;
 
our ( $from, $author, %metadata, @commands, $tmpdir, $tmpcount, $prefix, $tag, $filename, $platform );
 
$tmpdir = tempdir(CLEANUP => !$ENV{LEAVE_TMPDIR});
$tmpcount = 0;
$prefix = '';

$metadata{CMD} = ["/bin/bash"];
$filename = 'Dockerfile';
$platform = 'amd64';
GetOptions ('t=s' => \$tag,'f=s' => \$filename, 'p=s' => \$platform);
 
print "*** Working directory: $tmpdir\n" if $ENV{LEAVE_TMPDIR};
 
open DOCKERFILE, "<$filename" or die;
while ( <DOCKERFILE> ) {
  chomp;
 
  # handle long lines
  $_ = "$prefix$_";
  $prefix = '';
  if ( /\\$/ ) {
    s/\\$//;
    $prefix="$_\n";
    next;
  }
 
  s/^\s*//;
  /^#/ and next;
  /^$/ and next;
 
  my ($cmd, $args) = split(/\s+/, $_, 2);
  given ( uc $cmd ) {
    # building the image
    when ('FROM') { $from = $args }
    when ('RUN')  { push @commands, $args }
    when ('ADD')  {
      $tmpcount++;
      my ( $src, $dest ) = split ' ', $args, 2;
 
      if ( $src =~ /^https?:/ ) {
        my $basename = basename($src);
        my $target = "$tmpdir/dl/$tmpcount/$basename";
        make_path "$tmpdir/dl/$tmpcount";
        system('wget', '-O', $target, $src) == 0 or die;
        $src = $target;
      }
 
      my $local = "$tmpdir/$tmpcount";
 
      given ( $src ) {
        when ( /\.(tar(\.(gz|bz2|xz))?|tgz)$/ ) {
          mkdir $local;
          system('tar', '-C', $local, '-xf', $_) == 0 or die;
          push @commands, "mkdir -p '$dest'", "( cd /.data/$tmpcount ; cp -a . '$dest' )";
        }
        when ( -f $_ ) {
          $dest .= basename($_) if ( $dest =~ /\/$/ );
          system('cp', '-a', $_, $local) == 0 or die;
          push @commands, "mkdir -p '".dirname($dest)."'", "cp -a /.data/$tmpcount '$dest'";
        }
        when ( -d $_ ) {
          # Handle trailing slash combinations properly:
          # - `$src=/dir,  $dest=/foo  -> /foo`
          # - `$src=/dir,  $dest=/foo/ -> /foo/dir`
          # - `$src=/dir/, $dest=/foo  -> /foo`
          # - `$src=/dir/, $dest=/foo/ -> /foo`
          $dest .= basename($_) if ( $_ !~ /\/$/ && $dest =~ /\/$/ );
 
          system('cp', '-a', $_, $local) == 0 or die;
          push @commands, "mkdir -p '$dest'", "( cd /.data/$tmpcount ; cp -a . '$dest' )";
        }
        default { die }
      }
    }
 
    # image metadata
    when ('MAINTAINER') { $author = $args }
    when ('CMD')        { $metadata{CMD} =        eval { decode_json($args) } || ['sh', '-c', $args] }
    when ('ENTRYPOINT') { $metadata{ENTRYPOINT} = eval { decode_json($args) } || ['sh', '-c', $args] }
    when ('WORKDIR')    { $metadata{WORKDIR} = $args }
    when ('USER')       { $metadata{USER}       = $args }
    when ('EXPOSE')     { push @{ $metadata{EXPOSE} ||= [] },   split(' ',$args); }
    when ('ENV')        {
      my ( $k, $v ) = split(/s+/, $args, 2);
      push @commands, "export $k='$v'";
      push @{ $metadata{ENV} ||= [] }, "$k=$v";
    }
    when ('VOLUME')     {
      # This seems to be a NOP in `docker build`.
      # push @{ $metadata{VolumesFrom} ||= [] }, $args
    }
  }
}
close DOCKERFILE;
 
open SETUP, ">$tmpdir/setup.sh" or die;
print SETUP join("\n", "#!/bin/sh", "set -e -x", @commands), "\ntouch /.data/FINI\n";
close SETUP;
chmod 0755, "$tmpdir/setup.sh";
 
our @run = ('docker', 'run', "--platform=$platform", "--cidfile=$tmpdir/CID", '-v', "$tmpdir:/.data", $from, "/.data/setup.sh");
print "*** ", join(' ', @run), "\n";
system(@run) == 0 or die;
 
die "unfinished, not committing\n" unless -f "$tmpdir/FINI";
 
sleep 15; # docker container is not always immediately up to a commit, let's give it time to cool off.
 
open CID, "<$tmpdir/CID" or die;
our $cid = <CID>;
close CID;
 
# Convert metadata to a list of changes
foreach my $key (keys %metadata) {
    if (ref $metadata{$key} eq "ARRAY") {
        $metadata{$key} = join(" ", @{ $metadata{$key} });
    }
}
our @changes = map{qq{--change=$_ $metadata{$_}}} keys %metadata;
our @commit = ( 'docker', 'commit' );
push @commit, "--author=$author" if defined $author;
push @commit, @changes;
push @commit, $cid;
push @commit, $tag if defined $tag;
print "*** ", join(' ', @commit), "\n";
exec(@commit);
