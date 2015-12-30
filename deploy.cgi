#!/usr/bin/perl
use strict;
my %In = ();


my $Mailer = '/usr/lib/sendmail -t';


$In{email} = $ENV{QUERY_STRING} if ValidEmail($ENV{QUERY_STRING});
&ParseValues;
&CheckRequired;
&SendEmail;
&ThankYouPage;


sub ParseValues
{
        my $buffer;
        if ($ENV{REQUEST_METHOD} eq 'GET') { $buffer = $ENV{QUERY_STRING}; }
        else { read(STDIN,$buffer,$ENV{CONTENT_LENGTH}); }
        my @p = split(/&/,$buffer);
        foreach(@p)
        {
                $_ =~ tr/+/ /;
                my ($n,$v) = split(/=/,$_,2);
                $n =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
                $v =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
                $In{$n} = $v;
        }
} # sub ParseValues


sub CheckRequired
{
        my @e = ();
        $In{required} =~ s/^[ ,]*(.*?)[ ,]*$/$1/;
        $In{required} =~ s/\s*\,\s*/,/g;
        my @list = split /,+/,$In{required};
        for(@list) { push(@e,qq~Form field "$_" is required~) unless $In{$_} =~ /\w/; }
        push(@e,qq~"$In{email}" is not a valid email address~) unless ValidEmail($In{email});
        WebPageErrorMessage(@e) if @e;
} # sub CheckRequired


sub ValidEmail
{
        return 0 unless $_[0];
        return 0 if $_[0] =~ /(?:[\.\-\_]{2,})|(?:@[\.\-\_])|(?:[\.\-\_]@)|(?:\A\.)/;
        return 1 if $_[0] =~ /^[\w\.\-\_]+\@\[?[\w\.\-\_]+\.(?:[\w\.\-\_]{2,}|[0-9])\]?$/;
        return 0;
} # sub ValidEmail


sub WebPageErrorMessage
{
        my $s = join("</li>\n<li>",@_);
        print "Content-type: text/html\n\n";
        print <<HTML;
<html>
<body bgcolor="white">
<TABLE WIDTH="100%" HEIGHT="100%" BORDER="0" CELLPADDING="0" CELLSPACING="0">
<TR><TD WIDTH="100%" HEIGHT="100%" ALIGN="CENTER" VALIGN="MIDDLE">
<table border="0" cellpadding="0" cellspacing="0"><tr><td>
<h4>Message:</h4>
<ul>
<li>$s</li>
</ul>
</td></tr></table>
</TD></TR></TABLE>
</body></html>
HTML
        goto BOTTOM;
} # sub WebPageErrorMessage


sub SendEmail
{
        my $contenttype = 'plain';
        if($In{HTML} =~ /yes/i or $In{html} =~ /yes/i) { $contenttype = 'html'; }
        my $email;
        if($contenttype eq 'plain')
        {
                $email = <<THE_PLAIN_EMAIL;
From: me\@mydomain.com
To: [[email]]
Subject: [[firstname]], your requested "Widget by Me" blurb

Hello [[firstname]],

"Widget by Me" widgets get more and better wids than any
other widget on the market. And at an attractive price!

Buy a widget now because the current 20% discount special
is about to expire.

Send money to (bank drafts payable to "Me"):

        Me
        123 Road Ave.
        Anytown, Somewhere
        Country

Or, send money via http://PayPal.com to billing\@domain.com

Sincerely,

Your enthusiastic widget distributor!
THE_PLAIN_EMAIL
        }
        elsif($contenttype eq 'html')
        {
                $email = <<THE_HTML_EMAIL;
Mime-Version: 1.0
Content-type: text/html; charset="iso-8859-1"
From:stlunix_deploy_robot
To:user.name1\@domain.com,user.name2\@domain.com,user.name3\@domain.com,user.name4\@domain.com
#Cc:
Subject: A [[deployType]] server has been deployed.

<HTML>
<HEAD>
<TITLE>STLUNIX: System Build Request</TITLE>
<STYLE TYPE="text/css">
.body {font-family:arial,helvetica;font-size:12px;}
a:link {color:#000000;text-decoration:none;}
a:visited {color:#000000;}
a:hover {color:#000000;}
a:active {color:#000000;}
.rj {text-align:right;font-weight:bold;font-size:14px;}
.td {font-family:arial,helvetica;font-size:14px;}
</STYLE>
<BODY>
<FONT FACE="arial,helvetica">
<DIV STYLE="font-size:14px;">
Please submit a <A HREF="https://link_to_some_page.com/navpage.do" style="text-decoration:underline;">SNOW</A> Request with the information below:<BR/>
<DIV STYLE="font-size:12px;display:block;width:600px;background-color:#FFC000;color:#000000;">
<A HREF="http://wiki/wiki/index.php/article_name#article_section">Click here for instructions</A>
</DIV>
</DIV>
<P>
A [[deployType]] server has been deployed.<BR/>
<B>Details:</B>
<TABLE BORDER="0">
<TR><TD class="rj"><FONT FACE="arial,helvetica">Hostname:</FONT></TD>
    <TD><FONT FACE="arial,helvetica">[[deployHostname]]</FONT></TD></TR>
<TR><TD class="rj"><FONT FACE="arial,helvetica">Type:</FONT></TD>
    <TD><FONT FACE="arial,helvetica">[[deployType]]</FONT></TD></TR>
<TR><TD class="rj"><FONT FACE="arial,helvetica">Platform:</FONT></TD>
    <TD><FONT FACE="arial,helvetica">[[deployPlatform]]</FONT></TD></TR>
<TR><TD class="rj"><FONT FACE="arial,helvetica">Serial #:</FONT></TD>
    <TD><FONT FACE="arial,helvetica">[[deploySerial]]</FONT></TD></TR>
<TR><TD class="rj"><FONT FACE="arial,helvetica">Asset #:</FONT></TD>
    <TD><FONT FACE="arial,helvetica">[[deployAsset]]</FONT></TD></TR>
</TABLE>
<P>
Thank you,<BR />
STL Unix Team
</FONT>
</BODY>
</HTML>
THE_HTML_EMAIL
        }
        for(keys %In) { $email =~ s/\[\[$_\]\]/$In{$_}/sig; }
        $email =~ s/\[\[.*?\]\]//sig;
        open MAIL,"|$Mailer";
        print MAIL $email;
        close MAIL;
} # sub SendEmail


sub ThankYouPage
{
        if($In{thankyoupage} =~ /\w/)
        {
                $In{thankyoupage} = "http://$In{thankyoupage}" unless $In{thankyoupage} =~ m!^https?://!i;
                print "Location: $In{thankyoupage}\n\n";
                goto BOTTOM;
        }
        else
        {
                print "Content-type: text/html\n\n";
                print '<center>T H A N K &nbsp; Y O U !</center>';
        }
} # sub ThankYouPage


BOTTOM:
# end of script
