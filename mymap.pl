#!/usr/bin/env perl

use Mojolicious::Lite;
use DBI;
use Teng;
use Teng::Schema::Loader;

# herokuを利用する場合は$ENV{DATABASE_URL}に接続情報がある
$ENV{DATABASE_URL} ||= "postgres://syachi:passwd@/tmp:5432/gmap"; # 未定義の場合はローカルに接続
$ENV{DATABASE_URL} =~ m#\Apostgres://(\S+?):(\S+?)@(\S+?):(\d+)/(\S+?)\z#ms;
my ($user, $pass, $host, $port, $db) = ($1, $2, $3, $4, $5);

# DBIのハンドラを返す
my $dbh = DBI->connect(
  "dbi:Pg:host=$host;dbname=$db", $user, $pass,
  {PrintError => 0}
) || die "Could not connect";
helper dbh => sub { $dbh };

# Tengのハンドラを返す
my $teng = undef;
helper teng => sub { $teng };

# 初期化
helper init => sub {
  my $self = shift;
  # テーブルの情報を読み込む
  $teng = Teng::Schema::Loader->load(
    dbh => $self->dbh,
    namespace => 'MyApp::DB'
  );
};

# テーブルを作成して初期データを登録する
helper setup => sub {
  my $self = shift;

  # テーブルの情報を読み込む
  $self->init;

  # テーブルが存在していれば抜ける
  return 1 if defined $self->teng->schema->get_table('places');

  # テーブルが無い場合は作成する
  eval {
    $self->teng->do(q{
      CREATE TABLE places (
        id SERIAL PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        memo TEXT NOT NULL
      );
    });
  } || return undef;

  # テーブルを作成したので読み込み直す
  $self->init();

  # 初期データを登録する
  $self->teng->bulk_insert('places', [
    {name => '', address => '北海道札幌市白石区菊水元町7条1丁目10−21', memo => '',},
    {name => '', address => '北海道札幌市北区北18条西5丁目2−1'       , memo => '',},
    {name => '', address => '北海道札幌市西区発寒3条6−1−3'           , memo => '',},
    {name => '', address => '北海道札幌市北区北37条西4丁目2−6'       , memo => '',},
    {name => '', address => '北海道札幌市北区北25条西5丁目2−8'       , memo => '',},
    {name => '', address => '北海道札幌市北区北22条西5丁目2−32'      , memo => '',},
    {name => '', address => '北海道札幌市手稲区西宮の沢5条1丁目14−10', memo => '',},
  ]);

  return 1;
};

get '/' => sub {
  my $self = shift;
  $self->render('index');
};

get '/api/v1/addresses' => sub {
  my $self = shift;
  my @ret = ();
  foreach my $row ($self->teng->search('places')) {
    push @ret, {
      name    => $row->name,
      address => $row->address,
      memo    => $row->memo
    };
  }
  $self->render(json => \@ret);
};

post '/api/v1/addresses' => sub {
  my $self = shift;
  my $id = eval {
    $self->teng->fast_insert('places', $self->req->json);
  } || return undef;
  $self->render(json => {status => $id});
};

app->setup;
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
        map = new google.maps.Map($("#map").get(0), myOptions),
        infowindow = new google.maps.InfoWindow(),
        escape = function(val) {
          return $('<div />').text(val).html();
        };

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
              google.maps.event.addListener(marker, 'click', function(event) {
                var contents = [escape(row.name), escape(row.address), escape(row.memo)];
                infowindow.setContent(contents.filter(function(v) { return v != ''; }).join("<br>"));
                infowindow.open(map, marker);
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
