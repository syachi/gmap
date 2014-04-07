#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use JSON;

my @ret = ();
while(<DATA>) {
    chomp;
    push(@ret, {address => $_});
}
print "Content-type:application/json; charset=UTF-8\n\n";
print encode_json([@ret]);

__DATA__
北海道札幌市白石区菊水元町7条1丁目10−21
北海道札幌市北区北18条西5丁目2−1
北海道札幌市西区発寒3条6−1−3
北海道札幌市北区北37条西4丁目2−6
北海道札幌市北区北25条西5丁目2−8
北海道札幌市北区北22条西5丁目2−32
北海道札幌市手稲区西宮の沢5条1丁目14−10
