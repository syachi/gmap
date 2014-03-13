#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use Data::Section::Simple qw(get_data_section);
use Encode;
use JSON;
use LWP::UserAgent;
use Lingua::JA::Regular::Unicode qw/alnum_z2h/;
use Config::Any;

my $cfg = Config::Any->load_stems({stems => ["config"], use_ext => 1, flatten_to_hash => 1});
my($map, $init) = ($cfg->{"config.json"}{"map"}, $cfg->{"config.json"}{"initial"});

## 処理部分 ##
# 住所から緯度経度を取得する
my @locdata = split(/\n/, get_data_section('shop.dat'));
my @coord   = ();
foreach my $addr (@locdata){
	my ($formattedAddr, $lat, $lng) = &getCoordinates($addr);
	if (defined($formattedAddr)) {
		$formattedAddr =~ s/日本\,\s//g;	# 余計な文字を削除する
		push @coord, "{lat:\"$lat\", lng:\"$lng\", title:\"$formattedAddr\"}";
	} else {
		print STDOUT "Fatal error\n";
	}
}
my $posArray = join ",", @coord;

# HTMLの生成
my %contain = (
	"%%CENTER_LAT%%",  $init->{"lat"},
	"%%CENTER_LNG%%",  $init->{"lng"},
	"%%COORD_ARRAY%%", $posArray
);
my $html = get_data_section('index.html');
while (my ($key, $value) = each(%contain)) {
	$html =~ s/$key/$value/g;
}
print "Content-type: text/html\n\n";
print $html;
exit;

## 関数 ##
sub getCoordinates {
	my $adrs = $_[0];
	$adrs =~ s/[\－─ー－−]/\-/go;	# ハイフンを統一
	$adrs =~ s/(\W)/'%' . unpack('H2', $1)/ego; # URLエンコード
	my $ua = LWP::UserAgent->new();
	my $res = $ua->get($map->{"apiurl"}."?".$map->{"apiopt"}."&address=".$adrs);	# Google mapsにアクセス
	# エラー処理
	unless($res->is_success){
		return undef;
	}
	$res = decode_json($res->content);
	unless ($res->{status} eq 'OK') {
		return undef;
	}
	my $results = $res->{results};
	if(ref($results) ne 'ARRAY' or @$results != 1) {
		return undef;
	}
	# 値を返す
	return (
		$results->[0]->{formatted_address},	# 整形後の住所文字列
		$results->[0]->{geometry}->{location}->{lat}, #緯度
		$results->[0]->{geometry}->{location}->{lng}  #軽度
	);
}

## データ部分 ##
__DATA__
@@ index.html
<!doctype html>
<html lang="ja">
<head>
	<meta charset="UTF-8">
	<title>Show google map sample</title>
	<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
	<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=true"></script>
	<script type="text/javascript">
        window.onload = function () { initialize(); };
		function initialize() {
			var mapcenter = new google.maps.LatLng( %%CENTER_LAT%% , %%CENTER_LNG%% );
			var myOptions = {
				zoom: 12,
				center: mapcenter,
				mapTypeId: google.maps.MapTypeId.ROADMAP
			};
			var map = new google.maps.Map(document.getElementById("map"), myOptions);
			var markerData = [
				%%COORD_ARRAY%%
			];
			for (i = 0; i < markerData.length; i++){
				var marker = new google.maps.Marker({
					position: new google.maps.LatLng(markerData[i].lat, markerData[i].lng),
					title: markerData[i].title
				});
				marker.setMap(map);
			}
		}
	</script>
	<style type="text/css">
		html, body {margin: 0; padding: 0; height: 100%;}
		#map {width: 100%; height: 100%;}
	</style>
</head>
<body>
	<div id="map"></div>
</body>
</html>

@@ shop.dat
北海道札幌市白石区菊水元町7条1丁目10−21
北海道札幌市北区北18条西5丁目2−1
北海道札幌市西区発寒3条6−1−3
北海道札幌市北区北37条西4丁目2−6
北海道札幌市北区北25条西5丁目2−8
北海道札幌市北区北22条西5丁目2−32
北海道札幌市手稲区西宮の沢5条1丁目14−10
