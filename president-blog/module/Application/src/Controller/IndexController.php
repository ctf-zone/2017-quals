<?php
/**
 * @link      http://github.com/zendframework/ZendSkeletonApplication for the canonical source repository
 * @copyright Copyright (c) 2005-2016 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */

namespace Application\Controller;

use Zend\Mvc\Controller\AbstractActionController;
use Zend\View\Model\ViewModel;
use Zend\Db\Adapter\Adapter;
use Application\Service\PostsServiceInterface;
use Application\Model\PostsTable;
use Zend\Db\ResultSet\ResultSet;
use Zend\Session\Container;
use Zend\Db\Adapter\Exception\InvalidQueryException;
use Zend\Session\SessionManager;



class IndexController extends AbstractActionController
{
    public function __construct(Adapter $db, SessionManager $sm, Container $cn) {
        $this->db = $db;
        $this->sm = $sm;
        $this->containter = $cn;
    }

    public function indexAction() {
        return new ViewModel();
    }

    public function getPosts() {
        $res = $this->db->query('SELECT * FROM posts')->execute();
        $resultSet = new ResultSet();
        $resultSet->initialize($res);
        return $resultSet;
    }

    public function blogAction() {
        $view = new ViewModel();
        $view->posts = $this->getPosts();

        return $view;
    }

    public function adminAction() {
        $vm = new ViewModel();
        $request = $this->getRequest();
        $vm->error = False;
        if ($request->isPost()) {
            $login = $this->getRequest()->getPost("login");
            $password = $this->getRequest()->getPost("password");

            $query = $this->db->query("SELECT * FROM users where login = '$login' and password = '$password'");
            $resultSet = new ResultSet();
            try {
                $resultSet->initialize($query->execute());
                foreach ($resultSet as $user) {
                    $container = new Container('ContainerNamespace');
                    $container->user = $user->login;
                    return $this->redirect()->toRoute('report');
                }
                $vm->error = True;
            }
            catch (InvalidQueryException $e){
                $vm->error = True;
            }

        }

        return $vm;
    }
    public function reportAction() {
        
        $container = new Container('ContainerNamespace');
        if ($container->user != "admin") {
            return $this->redirect()->toRoute('admin');
        }
        $vm = new ViewModel();
        $vm->subject = "Report from ". date('d-m-Y H-i');
        $vm->sent = False;
        $request = $this->getRequest();
        $vm->sent = "";
        if ($request->isPost()) {
            
                $subject = $this->getRequest()->getPost("subject");
                $encoding = $this->getRequest()->getPost("encoding") or 'UTF-8';
                $to = "briskly@ya.ru";
                $headers = "Subject: " . $subject. "\r\n" .
                    'From: webmaster@example.com' . "\r\n".
                    'Content-type: text/xml'. "\r\n";
                $message = "Testing something new\n";
                
                $str = "<?xml version=\"1.0\" encoding=\"$encoding\"?> 
<report>
    <about>
        <date>date</date>
        <subject>$subject</subject>
    </about>
    <posts>
    </posts>
</report>
";          
                $xml = @simplexml_load_string($str, null, LIBXML_NOENT | LIBXML_DTDLOAD);
                if ($xml) {
                    $posts = $xml->xpath("/report/posts")[0];
                    foreach ($this->getPosts() as $post) {
                        $element = $posts->addChild("post");
                        $element->addChild("title", $post->title);
                        $element->addChild("body", $post->body);
                        
                    }
                    $message = $xml->asXML();
                    $subject = "";
                    mail($to, $subject, $message, $headers);
                    $vm->sent = "yes";
                } else {
                    $vm->sent = "no";
                }

                
            
                
          
        }
        
        return $vm;
    }
}
