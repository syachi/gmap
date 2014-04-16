#!/usr/bin/env perl

use Mojolicious::Lite;
use DBI;

# herokuを利用する場合は$ENV{DATABASE_URL}に接続情報がある
$ENV{DATABASE_URL} ||= "postgres://syachi:passwd@/tmp:5432/gmap"; # 未定義の場合はローカルに接続
$ENV{DATABASE_URL} =~ m#\Apostgres://(\S+?):(\S+?)@(\S+?):(\d+)/(\S+?)\z#ms;
my ($user, $pass, $host, $port, $db) = ($1, $2, $3, $4, $5);

# データベースに接続する
my $dbh = DBI->connect("dbi:Pg:host=$host;dbname=$db", $user, $pass, {PrintError => 0}) || die "Could not connect";

# データベースのハンドラを返す
helper db => sub { $dbh };

# レコードを登録する
helper insert => sub {
  my $self = shift;
  my ($address) = @_;
  my $sth = $self->db->prepare('INSERT INTO places (address) VALUES (?)') || return undef;
  $sth->execute($address) || return undef;
  return 1;
};

# 登録されているデータを返す
helper select => sub {
  my $self = shift;
  my $sth = $self->db->prepare('SELECT address FROM places') || return undef;
  $sth->execute() || return undef;
  return $sth->fetchall_arrayref(+{});
};

# テーブルを作成して初期データを登録する
helper create_table => sub {
  my $self = shift;
  warn "CREATE TABLE";
  $self->db->do('CREATE TABLE places (id serial primary key, address text)') || return undef;
  # 初期データ
  $self->insert('北海道札幌市白石区菊水元町7条1丁目10−21');
  $self->insert('北海道札幌市北区北18条西5丁目2−1');
  $self->insert('北海道札幌市西区発寒3条6−1−3');
  $self->insert('北海道札幌市北区北37条西4丁目2−6');
  $self->insert('北海道札幌市北区北25条西5丁目2−8');
  $self->insert('北海道札幌市北区北22条西5丁目2−32');
  $self->insert('北海道札幌市手稲区西宮の沢5条1丁目14−10');
  return 1;
};

# SELECTに失敗した場合はテーブルを作成する
app->select || app->create_table;

get '/' => sub {
  my $self = shift;
  $self->render('index');
};

get '/api/v1/addresses' => sub {
  my $self = shift;
  $self->render(json => $self->select);
};

app->start;

__DATA__

@@ index.html.ep
<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>Show google map sample</title>
  <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
  <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>
  <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
  <script type="text/javascript">
    $(function () {
      var mapcenter = new google.maps.LatLng(43.0631485, 141.3540735),
        geocoder = new google.maps.Geocoder(),
        myOptions = {
          zoom: 12,
          center: mapcenter,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        },
        addresses = [],
        map = new google.maps.Map($("#map").get(0), myOptions);
      $.ajax({
        type: 'GET',
        url: 'api/v1/addresses',
        dataType: 'json',
        success: function(rows) {
          $.each(rows, function(i, row) {
            geocoder.geocode({"address": row.address, "region": "jp"}, function (results, status) {
              if (status !== google.maps.GeocoderStatus.OK) return;
              var marker = new google.maps.Marker({
                map: map,
                position: results[0].geometry.location
              });
            });
          });
        }
      });
    });
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
