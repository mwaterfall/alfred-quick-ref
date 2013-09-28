//
//  AppDelegate.h
//  QuickRefQL
//
//  Created by Michael Waterfall on 26/09/2013.
//  Copyright (c) 2013 Michael Waterfall. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import <QuickLook/QuickLook.h>
#import <Quartz/Quartz.h>

@interface AppDelegate : NSObject <NSApplicationDelegate, QLPreviewPanelDelegate, QLPreviewPanelDataSource>

@property (assign) IBOutlet NSWindow *window;
@property (retain) QLPreviewPanel *previewPanel;

@end
