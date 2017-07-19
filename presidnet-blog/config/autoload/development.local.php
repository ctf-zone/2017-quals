<?php
/**
 * Local Configuration Override for DEVELOPMENT MODE.
 *
 * This configuration override file is for providing configuration to use while
 * in development mode. Run:
 *
 * <code>
 * $ composer development-enable
 * </code>
 *
 * from the project root to copy this file to development.local.php and enable
 * the settings it contains.
 *
 * You may also create files matching the glob pattern `{,*.}{global,local}-development.php`.
 */

return [
    'view_manager' => [
        'display_not_found_reason' => false,
        'display_exceptions'       => false,
        'doctype'                  => 'HTML5',
        'not_found_template'       => 'error/404',
        // 'exception_template'       => 'error/index',
        // 'template_map' => [
        //     'layout/layout'           => __DIR__ . '/../../module/Application/view/layout/layout.phtml',
        //     'application/index/index' => __DIR__ . '/../../module/Application/view/application/index/index.phtml',
        //     'error/404'               => __DIR__ . '/../../module/Application/view/error/404.phtml',
        //     'error/index'             => __DIR__ . '/../../module/Application/view/error/index.phtml',
        // ],
        // 'template_path_stack' => [
        //     __DIR__ . '/../../module/Application/view',
        // ],
    ],
];
