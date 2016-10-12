pkgname=jmf
pkgver=0.1.1
pkgrel=1
pkgdesc="Match listings to unfilled openings."
arch=('any')
url=""
license=('GPLv3')
groups=()
depends=('python>=3', 'python-requests')
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
  # cd "$srcdir/jmf" # cd "$srcdir/jmf-$pkgver"
  python setup.py install --root="$pkgdir/" --optimize=1
  install -Dm 644 $srcdir/jmf.service $pkgdir/usr/lib/systemd/user/jmf.service
  install -Dm 644 $srcdir/jmf.timer $pkgdir/usr/lib/systemd/user/jmf.timer
  install -Dm 755 $srcdir/jmf.py $pkgdir/usr/bin/jmf
  install -Dm 755 $srcdir/jmf-service.py $pkgdir/usr/bin/jmf-service
}

# vim:set ts=2 sw=2 et:
