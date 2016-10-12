pkgname=what
pkgver=0.1.1
pkgrel=1
pkgdesc="Match listings to unfilled openings."
arch=('any')
url=""
license=('GPLv3')
groups=()
depends=('python>=3', 'python-openings')
makedepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=()
install=
source=()
noextract=()
md5sums=() #generate with 'makepkg -g'


build() {
	cd $srcdir
	python setup.py sdist
}

package() {
  # cd "$srcdir/what" # cd "$srcdir/what-$pkgver"
  python setup.py install --root="$pkgdir/" --optimize=1
  install -Dm 644 $srcdir/what.service $pkgdir/usr/lib/systemd/user/what.service
  install -Dm 644 $srcdir/what.timer $pkgdir/usr/lib/systemd/user/what.timer
  install -Dm 755 $srcdir/what.py $pkgdir/usr/bin/what
  install -Dm 755 $srcdir/what-service.py $pkgdir/usr/bin/what-service
}

# vim:set ts=2 sw=2 et:
