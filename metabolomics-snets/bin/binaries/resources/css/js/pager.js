// +------------------------------------------------------------+
// |               HTML Table Pager Version 1.01                |
// +------------------------------------------------------------+
// | Last Modified:                  19-Jun-2006                |
// | Web Site:                       http://joeli.t35.com/      |
// | Web Site (2):                   http://joeli.27h.org/      |
// | EMail:                          licp at hotmail dot com    |
// +------------------------------------------------------------+
// |       Copyright 2006  Joe Li     All Rights Reserved.      |
// |     Permission given to use this script in ANY kind of     |
// |      applications if header lines are left unchanged.      |
// +------------------------------------------------------------+

function Pager(id, PageSize) {
	this._o = document.getElementById(id);
	if (this._o) this._displayElement(this._o, false);
	this.RecordCount = 0;
	this.PageCount = 0;
	this.PageSize = parseInt(PageSize);
	this._setRecordCount();
	this._setPageCount();
	this.AbsolutePage = (this.RecordCount > 0 ? 1: 0);
	this._currentPage = 0;
}

Pager.prototype.reload = function() {
	this._setRecordCount();
	this.display();
};

Pager.prototype._setRecordCount = function() {
	this.RecordCount = (this._o && this._o.rows ? this._o.rows.length - 1: 0);
};

Pager.prototype._setPageCount = function() {
	if (this.RecordCount <= 0) {
		this.PageCount = 0;
	} else {
		this.PageSize = parseInt(this.PageSize);
		if (isNaN(this.PageSize) || this.PageSize < 1) this.PageSize = 10;
		this.PageCount = Math.ceil(this.RecordCount / this.PageSize);
	}
};

Pager.prototype.toString = function() {
	return '<p>Pager:' + '<br />' +
		'RecordCount = ' + this.RecordCount + '<br />' +
		'PageSize = ' + this.PageSize + '<br />' +
		'PageCount = ' + this.PageCount + '<br />' +
		'AbsolutePage = ' + this.AbsolutePage + '</p>';
};

Pager.prototype._displayElement = function(e, bool) {
	if (!e || !e.style) return;
	e.style.display = (bool? '': 'none');
};

Pager.prototype.display = function() {
	this._setPageCount();
	if (this.RecordCount <= 0 || this.PageCount <= 0) return;
	this.AbsolutePage = parseInt(this.AbsolutePage);
	if (isNaN(this.AbsolutePage) || this.AbsolutePage < 1 || this.AbsolutePage > this.PageCount) this.AbsolutePage = 1;
	/* remain unchanged */
	if (this._currentPage == this.AbsolutePage) return;
	this._displayElement(this._o, false);
	this._displayElement(this._o.rows[0], true);
	if (this._currentPage > 0) {
		for (var i = (this._currentPage - 1) * this.PageSize + 1; i <= this._currentPage * this.PageSize; i++) this._displayElement(this._o.rows[i], false);
	} else {
		for (var i = 1; i <= this.RecordCount; i++) this._displayElement(this._o.rows[i], false);
	}
	if (this.AbsolutePage > 0) for (var i = (this.AbsolutePage - 1) * this.PageSize + 1; i <= this.AbsolutePage * this.PageSize; i++) this._displayElement(this._o.rows[i], true);
	this._currentPage = this.AbsolutePage;
	this._displayElement(this._o, true);
};

Pager.prototype.prevPage = function() {
	if (this.AbsolutePage - 1 >= 1) {
		this.AbsolutePage--;
		this.display();
	}
};

Pager.prototype.nextPage = function() {
	if (this.AbsolutePage + 1 <= this.PageCount) {
		this.AbsolutePage++;
		this.display();
	}
};

Pager.prototype.navBar = function(varName, eName) {
	var e = document.getElementById(eName);
	if (!e) return;
	this._setPageCount();
	if (this.PageCount <= 1) return;
	var s = '';
	s += '<a href="javascript:' + varName + '.prevPage()">' + '&laquo;' + '</a> ';
	for (var i = 1; i <= this.PageCount; i++) s += '<a href="javascript:' + varName + '.display()" onclick="' + varName + '.AbsolutePage=' + i + ';">' + i + '</a> ';
	s += '<a href="javascript:' + varName + '.nextPage()">' + '&raquo;' + '</a> ';
	e.innerHTML = s;
};