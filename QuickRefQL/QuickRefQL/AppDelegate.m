//
//  AppDelegate.m
//  QuickRefQL
//  Very hacky but working app that opens a URL in quick look and quits when it's dismissed
//
//  Created by Michael Waterfall on 26/09/2013.
//  Copyright (c) 2013 Michael Waterfall. All rights reserved.
//

#import "AppDelegate.h"
#import <QuickLook/QuickLook.h>
#import <Quartz/Quartz.h>

NSString *filePath; // it's only ever one file path anyway!

@interface QLFile : NSObject <QLPreviewItem>

@property (readonly) NSString *previewItemTitle;
@property (readonly) NSURL *previewItemURL;

@end

@implementation QLFile

- (NSString *)previewItemTitle {
    return filePath;
}

- (NSURL *)previewItemURL {
    return [NSURL fileURLWithPath:filePath];
}

@end

@implementation AppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    [[NSApplication sharedApplication] activateIgnoringOtherApps: YES];
    NSArray *args = [[NSProcessInfo processInfo] arguments];
    if (args.count < 2) exit(1);
    filePath = [args objectAtIndex:1];
    if (![[NSFileManager defaultManager] fileExistsAtPath:filePath]) exit(0);
    if ([QLPreviewPanel sharedPreviewPanelExists] && [[QLPreviewPanel sharedPreviewPanel] isVisible]) {
        [[QLPreviewPanel sharedPreviewPanel] orderOut:nil];
    } else {
        [[QLPreviewPanel sharedPreviewPanel] updateController]; //not sure if this is really needed as it should update itself…
        [[QLPreviewPanel sharedPreviewPanel] makeKeyAndOrderFront:nil];
    }
}

- (BOOL)acceptsPreviewPanelControl:(QLPreviewPanel *)panel
{
    //note that this methods indeed gets called because NSApp's
    //delegate is in the responder chain.
    return YES;
}

- (void)beginPreviewPanelControl:(QLPreviewPanel *)panel
{
    self.previewPanel = panel; //set an ivar
    [panel setDataSource:self];
}

- (void)endPreviewPanelControl:(QLPreviewPanel *)panel
{
    self.previewPanel = nil;
    exit(0);
}

- (NSInteger)numberOfPreviewItemsInPreviewPanel:(QLPreviewPanel *)panel
{
    //return a number of your choice (depends on your own app)
    return 1;
}

- (id <QLPreviewItem>)previewPanel:(QLPreviewPanel *)panel
                previewItemAtIndex:(NSInteger)index
{
    //return an object of your choice (depends on your app)
    return [QLFile new];
}

- (void)handleCurrentFileItemsSelectionChange:(NSNotification *)note
{
    [self.previewPanel reloadData]; //referring to the ivar
}

@end
