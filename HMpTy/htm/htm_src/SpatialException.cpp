//# SpatialException.cpp
//#
//# Author:    John Doug Reynolds, P. Kunszt
//# 
//# Creation:  March 1997
//#
//#
//# (c) Copyright The Johns Hopkins University 1995
//# All Rights Reserved
//#
//# The software and information contained herein are proprietary to The
//# Johns Hopkins University, Copyright 1995.  This software is furnished
//# pursuant to a written license agreement and may be used, copied,
//# transmitted, and stored only in accordance with the terms of such
//# license and with the inclusion of the above copyright notice.  This
//# software and information or any other copies thereof may not be
//# provided or otherwise made available to any other person.
//#
//#
//# Modification history:
//#
//# Oct. 1998, P. Kunszt : remove Rogue Wave C-string dependency
//#                        almost all the interface had to be rewritten.
//#			   Also, use some of the inheritance to avoid
//#			   code duplication. Introduced defaultstr[].

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <SpatialException.h>

/* --- SpatialException methods ------------------------------------------------- */
const char *
SpatialException::defaultstr[] = {
  "SDSS Science Archive",
  "generic exception",			// These specialized exceptions are
  "unimplemented functionality",	// currently implemented. If no string
  "failed operation",			// is given, this is the standard
  "array bounds violation",		// message.
  "interface violation"
};

#define CONTEXT 	0		// indices of exceptions
#define GENERIC 	1
#define UNIMPLEMENTED 	2
#define FAILURE 	3
#define BOUNDS 		4
#define INTERFACE	5

SpatialException::~SpatialException() throw() {
  if(str_)free(str_);
}

SpatialException::SpatialException( const char *cstr, int defIndex ) throw()
{
   try {
     if ( cstr ) {
       str_ = new char[slen(cstr) + 1];
       strcpy(str_,cstr);
     } else {
       str_ = new char[50];
       snprintf(str_,sizeof(str_)*5,"%s : %s",defaultstr[CONTEXT],defaultstr[defIndex]);
     }
   }
   catch (...) {
     delete[] str_;
   }
}

SpatialException::SpatialException( const char *context, const char *because,
			  int defIndex) throw()
{
   try {
     const char * tmpc, * tmpb;
     tmpc = context ? context : defaultstr[CONTEXT];
     tmpb = because ? because : defaultstr[defIndex];
     str_ = new char[slen(tmpc) + slen(tmpb) + 50]; // allow extensions
     snprintf(str_,sizeof(str_)*5,"%s : %s",tmpc,tmpb);
   }
   catch (...) {
     delete[] str_;
   }
}

SpatialException::SpatialException( const SpatialException& oldX ) throw()
{
  try {
    if(oldX.str_) {
      str_ = new char[slen(oldX.str_) + 1];
      strcpy(str_,oldX.str_);
    }
  }
  catch (...) {
    delete[] str_;
  }
}

SpatialException& SpatialException::operator=( const SpatialException& oldX ) throw()
{
   try {
     if(&oldX != this) { // beware of self-assignment
       if(oldX.str_) {
	 str_ = new char[slen(oldX.str_) + 1];
	 strcpy(str_,oldX.str_);
       }
     }
   }
   catch (...) {
     delete[] str_;
   }
   return *this;
}

const char *SpatialException::what() const throw()
{
   try {
      return str_;
   }
   catch (...) {
      return "";
   }
}

int SpatialException::slen(const char *str) const
{
  if(str)return strlen(str);
  return 0;
}

void SpatialException::clear()
{
  if(str_)delete[] str_;
}
/* --- SpatialUnimplemented methods --------------------------------------------- */

SpatialUnimplemented::SpatialUnimplemented( const char *cstr ) throw()
: SpatialException(cstr,UNIMPLEMENTED)
{
}

SpatialUnimplemented::SpatialUnimplemented( const char *context, const char *because )
   throw()
  : SpatialException(context, because, UNIMPLEMENTED)
{
}

SpatialUnimplemented::SpatialUnimplemented( const SpatialUnimplemented& oldX ) throw()
  : SpatialException(oldX)
{
}

/* --- SpatialFailure methods --------------------------------------------------- */

SpatialFailure::SpatialFailure( const char *cstr ) throw()
  : SpatialException(cstr, FAILURE)
{
}

SpatialFailure::SpatialFailure( const char *context, const char *because ) throw()
  : SpatialException(context,because,FAILURE)
{
}

SpatialFailure::SpatialFailure( const char *context, const char *operation
		      , const char *resource, const char *because ) throw()
{
   try {
      delete[] str_;
      if ( !operation && !resource && !because ) {
	 if ( !context ) context = defaultstr[CONTEXT];
	 because = "failed operation";
      }
      str_ = new char[ slen(context) + slen(operation) + slen(resource)
		      + slen(because) + 50];
      *str_ = '\0';
      if ( !context )
	context = defaultstr[CONTEXT];
      snprintf(str_,sizeof(str_)*5,"%s: ",context);
      if ( operation ) {
	 snprintf(str_,sizeof(str_)*5,"%s %s failed ",str_, operation);
      }
      if ( resource ) {
	 if(operation)
	   snprintf(str_,sizeof(str_)*5,"%s on \"%s\"",str_,resource);
	 else
	   snprintf(str_,sizeof(str_)*5,"%s trouble with \"%s\"",str_,resource);
      }
      if ( because ) {
	 if ( operation || resource )
	   snprintf(str_,sizeof(str_)*5,"%s because %s",str_,because);
	 else
	   snprintf(str_,sizeof(str_)*5,"%s %s",str_,because);
      }
   }
   catch (...) {
     delete[] str_;
   }
}

SpatialFailure::SpatialFailure( const SpatialFailure& oldX ) throw()
  : SpatialException(oldX)
{
}

/* --- SpatialBoundsError methods ----------------------------------------------- */

SpatialBoundsError::SpatialBoundsError( const char *cstr ) throw()
  : SpatialException(cstr,BOUNDS)
{
}

SpatialBoundsError::SpatialBoundsError( const char *context, const char *array
			      , int32 limit, int32 index ) throw()
  : SpatialException(context,array,BOUNDS)
{
   try {
     if ( limit != -1 ) {
       if ( array )
	   snprintf(str_,sizeof(str_)*5,"%s[%d]",str_,index);
	 else
	   snprintf(str_,sizeof(str_)*5, "%s array index %d ",str_, index );

	 if ( index > limit ) {
	   snprintf(str_,sizeof(str_)*5, "%s over upper bound by %d",str_, index - limit );
	 }
	 else {
	   snprintf(str_,sizeof(str_)*5, "%s under lower bound by %d",str_, limit - index );
	 }
      }
   }
   catch (...) {
     delete[] str_;
   }
}

SpatialBoundsError::SpatialBoundsError( const SpatialBoundsError& oldX ) throw()
  : SpatialException(oldX)
{
}

/* --- SpatialInterfaceError methods -------------------------------------------- */

SpatialInterfaceError::SpatialInterfaceError( const char *cstr ) throw()
  : SpatialException(cstr,INTERFACE)
{
}

SpatialInterfaceError::SpatialInterfaceError( const char *context, const char *because )
   throw()
  : SpatialException(context,because,INTERFACE)
{
}

SpatialInterfaceError::SpatialInterfaceError( const char *context, const char *argument
				 , const char *because ) throw()
{
   try {
      delete[] str_;
      str_ = new char[slen(context) + slen(argument) + slen(because) + 128];
      *str_ = '\0';
      if ( !context )
	       context = defaultstr[CONTEXT];
      snprintf(str_,sizeof(str_)*5,"%s: ",context);
      if ( argument && because ) {
      	 snprintf(str_,sizeof(str_)*5,"%s argument \"%s\" is invalid because %s ",str_,
      		 argument, because);
      }
      else if ( argument && !because ) {
      	 snprintf(str_,sizeof(str_)*5,"%s invalid argument \"%s\" ",str_,
      		 argument);
      }
      else if ( !argument ) {
      	if(because)
      	  snprintf(str_,sizeof(str_)*5,"%s %s",str_,because);
      	else
      	  snprintf(str_,sizeof(str_)*5,"%s interface violation",str_);
         }
      }
   catch (...) {
     delete[] str_;
   }
}

SpatialInterfaceError::SpatialInterfaceError( const SpatialInterfaceError& oldX ) throw()
  : SpatialException(oldX)
{
}
